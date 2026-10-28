"""Strict read-only SQL validation and bounded FocusBloom history retrieval."""

from __future__ import annotations

import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import RAG_DEADLINE_MS, RAG_MAX_COLUMNS, RAG_MAX_PAYLOAD_BYTES, RAG_MAX_ROWS
from .database import DEMO_PROFILE_ID


class QueryRejected(Exception):
    """A model-proposed query is outside the approved read-only grammar."""


class RetrievalFailure(Exception):
    """A sanitized retrieval failure, including deadline and snapshot failures."""


ALLOWED_COLUMNS = {
    "activity_sessions": {
        "session_id", "profile_id", "activity_type", "status", "started_at", "ended_at",
        "duration_ms", "difficulty", "motion_mode", "guidance_level", "perspective_progress",
        "alternative_save_state", "seed_save_state", "model_status", "version",
    },
    "perspective_artifacts": {
        "artifact_id", "profile_id", "session_id", "interpretation_text", "alternative_text",
        "alternative_source", "observer_mode", "saved_at", "updated_at",
    },
    "next_step_seeds": {
        "seed_id", "profile_id", "session_id", "situation_text", "action_text",
        "formatted_plan", "source", "saved_at", "updated_at",
    },
    "preferences": {
        "profile_id", "motion_mode", "guidance_level", "difficulty",
        "remember_preferences", "version", "updated_at",
    },
}
ALLOWED_FUNCTIONS = {"count", "min", "max"}
SQL_KEYWORDS = {
    "select", "from", "where", "and", "group", "by", "order", "limit", "as",
    "asc", "desc", "is", "null", "not", "in", "like", "collate", "nocase",
}
FORBIDDEN = re.compile(
    r"\b(?:with|insert|update|delete|replace|create|alter|drop|pragma|attach|detach|"
    r"vacuum|reindex|analyze|begin|commit|rollback|savepoint|release|join|union|"
    r"intersect|except|returning|window|over|load_extension)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ValidatedQuery:
    sql: str
    parameters: dict[str, str | int]
    table: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class RetrievedRows:
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    row_references: tuple[int, ...]


def _split_selected(value: str) -> list[str]:
    parts, depth, start = [], 0, 0
    for index, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise QueryRejected("unbalanced expression")
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    if depth != 0:
        raise QueryRejected("unbalanced expression")
    parts.append(value[start:].strip())
    return parts


def validate_query(sql: str, parameters: dict[str, str | int]) -> ValidatedQuery:
    """Accept only one deliberately small SELECT grammar; CTEs are not approved."""

    if not isinstance(sql, str) or not sql.strip() or len(sql) > 2000:
        raise QueryRejected("query length")
    statement = " ".join(sql.strip().split())
    lowered = statement.casefold()
    if not lowered.startswith("select ") or ";" in statement or "--" in statement or "/*" in statement:
        raise QueryRejected("single select required")
    if FORBIDDEN.search(lowered) or re.search(r"\bfrom\s*\(", lowered):
        raise QueryRejected("forbidden SQL construct")
    if "'" in statement or '"' in statement or "`" in statement or "[" in statement:
        raise QueryRejected("literal or quoted identifier")
    limit_match = re.search(r"\sLIMIT\s+(\d+)\s*$", statement, re.IGNORECASE)
    if limit_match is None:
        raise QueryRejected("one final limit required")
    limit = int(limit_match.group(1))
    if not 1 <= limit <= RAG_MAX_ROWS or len(re.findall(r"\blimit\b", lowered)) != 1:
        raise QueryRejected("limit outside boundary")
    without_limit = statement[: limit_match.start()]
    match = re.fullmatch(
        r"SELECT\s+(.+?)\s+FROM\s+([a-z_][a-z0-9_]*)\s+WHERE\s+(.+?)(?:\s+GROUP\s+BY\s+(.+?))?(?:\s+ORDER\s+BY\s+(.+?))?",
        without_limit,
        re.IGNORECASE,
    )
    if match is None:
        raise QueryRejected("unsupported select structure")
    selected_text, table, where_text, group_text, order_text = match.groups()
    table = table.casefold()
    if table not in ALLOWED_COLUMNS:
        raise QueryRejected("unapproved table")
    if re.search(r"\bprofile_id\s*=\s*:profile_id\b", where_text, re.IGNORECASE) is None:
        raise QueryRejected("trusted profile scope required")
    if re.search(r"\bor\b", where_text, re.IGNORECASE):
        raise QueryRejected("OR is outside the approved grammar")
    conditions = re.split(r"\s+AND\s+", where_text, flags=re.IGNORECASE)
    for condition in conditions:
        comparison = re.fullmatch(
            r"\s*([a-z_][a-z0-9_]*)\s*(=|!=|<>|<=|>=|<|>|LIKE)\s*"
            r":([a-z][a-z0-9_]{0,30})\s*",
            condition,
            re.IGNORECASE,
        )
        null_check = re.fullmatch(
            r"\s*([a-z_][a-z0-9_]*)\s+IS\s+(?:NOT\s+)?NULL\s*",
            condition,
            re.IGNORECASE,
        )
        column = (comparison or null_check).group(1).casefold() if comparison or null_check else None
        if column not in ALLOWED_COLUMNS[table]:
            raise QueryRejected("unsupported where predicate")

    selected = _split_selected(selected_text)
    if not 1 <= len(selected) <= RAG_MAX_COLUMNS:
        raise QueryRejected("selected column boundary")
    output_columns: list[str] = []
    aliases: set[str] = set()
    for expression in selected:
        column_match = re.fullmatch(
            r"([a-z_][a-z0-9_]*)(?:\s+AS\s+([a-z_][a-z0-9_]*))?",
            expression,
            re.IGNORECASE,
        )
        aggregate_match = re.fullmatch(
            r"(COUNT|MIN|MAX)\s*\(\s*(\*|[a-z_][a-z0-9_]*)\s*\)(?:\s+AS\s+([a-z_][a-z0-9_]*))?",
            expression,
            re.IGNORECASE,
        )
        if column_match:
            column, alias = column_match.groups()
            if column.casefold() not in ALLOWED_COLUMNS[table]:
                raise QueryRejected("unapproved selected column")
            output = (alias or column).casefold()
        elif aggregate_match:
            function, column, alias = aggregate_match.groups()
            if function.casefold() not in ALLOWED_FUNCTIONS:
                raise QueryRejected("unapproved function")
            if column != "*" and column.casefold() not in ALLOWED_COLUMNS[table]:
                raise QueryRejected("unapproved aggregate column")
            output = (alias or f"{function.casefold()}_{column.casefold()}").casefold()
        else:
            raise QueryRejected("unsupported selected expression")
        if output in aliases:
            raise QueryRejected("duplicate output column")
        aliases.add(output)
        output_columns.append(output)

    placeholders = set(re.findall(r":([a-z][a-z0-9_]{0,30})", statement, re.IGNORECASE))
    if "profile_id" not in placeholders or "profile_id" in parameters:
        raise QueryRejected("profile parameter is backend owned")
    if placeholders - {"profile_id", *parameters.keys()} or set(parameters) != placeholders - {"profile_id"}:
        raise QueryRejected("parameter mismatch")
    where_without_params = re.sub(r":[a-z][a-z0-9_]{0,30}", "", where_text, flags=re.IGNORECASE)
    if re.search(r"(?<![A-Za-z_])\d+(?:\.\d+)?(?![A-Za-z_])", where_without_params):
        raise QueryRejected("literal values are not permitted")
    for value in parameters.values():
        if isinstance(value, str) and len(value) > 120:
            raise QueryRejected("parameter too large")
        if not isinstance(value, (str, int)) or isinstance(value, bool):
            raise QueryRejected("parameter type")

    identifiers = set(re.findall(r"\b[a-z_][a-z0-9_]*\b", statement, re.IGNORECASE))
    allowed_identifiers = (
        SQL_KEYWORDS | {table} | ALLOWED_COLUMNS[table] | ALLOWED_FUNCTIONS |
        aliases | set(parameters) | {"profile_id"}
    )
    if {item.casefold() for item in identifiers} - allowed_identifiers:
        raise QueryRejected("unapproved identifier")
    if group_text:
        for column in [part.strip().casefold() for part in group_text.split(",")]:
            if column not in ALLOWED_COLUMNS[table]:
                raise QueryRejected("unapproved group column")
    if order_text:
        for part in order_text.split(","):
            order_match = re.fullmatch(
                r"\s*([a-z_][a-z0-9_]*)(?:\s+(ASC|DESC))?\s*", part, re.IGNORECASE
            )
            if order_match is None or order_match.group(1).casefold() not in ALLOWED_COLUMNS[table] | aliases:
                raise QueryRejected("unapproved order expression")
    trusted = {**parameters, "profile_id": DEMO_PROFILE_ID}
    return ValidatedQuery(statement, trusted, table, tuple(output_columns))


def _authorizer(action: int, arg1: str | None, arg2: str | None, _database: str | None, _source: str | None) -> int:
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        if arg1 in ALLOWED_COLUMNS and arg2 in ALLOWED_COLUMNS[arg1]:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:
        function = (arg2 or arg1 or "").casefold()
        return sqlite3.SQLITE_OK if function in ALLOWED_FUNCTIONS else sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_DENY


def execute_read_only(database_path: Path, query: ValidatedQuery) -> RetrievedRows:
    """Execute a validated statement through a separate, default-deny read-only connection."""

    uri = f"{database_path.resolve().as_uri()}?mode=ro"
    deadline = time.monotonic() + (RAG_DEADLINE_MS / 1000)
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=0.1)
        connection.row_factory = sqlite3.Row
        connection.enable_load_extension(False)
        connection.execute("PRAGMA query_only = ON")
        connection.execute("PRAGMA trusted_schema = OFF")
        before = connection.execute("PRAGMA data_version").fetchone()[0]
        connection.set_authorizer(_authorizer)
        connection.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 100)
        cursor = connection.execute(query.sql, query.parameters)
        description = cursor.description or ()
        if not 1 <= len(description) <= RAG_MAX_COLUMNS:
            raise RetrievalFailure("column boundary")
        columns = tuple(item[0] for item in description)
        rows = cursor.fetchmany(RAG_MAX_ROWS + 1)
        if len(rows) > RAG_MAX_ROWS:
            raise RetrievalFailure("row boundary")
        normalized = tuple(tuple(row[column] for column in columns) for row in rows)
        payload = json.dumps(
            {"columns": columns, "rows": normalized}, separators=(",", ":"), default=str
        ).encode("utf-8")
        if len(payload) > RAG_MAX_PAYLOAD_BYTES:
            raise RetrievalFailure("payload boundary")
        connection.set_progress_handler(None, 0)
        connection.set_authorizer(None)
        after = connection.execute("PRAGMA data_version").fetchone()[0]
        if before != after:
            raise RetrievalFailure("snapshot changed")
        return RetrievedRows(columns, normalized, tuple(range(1, len(normalized) + 1)))
    except QueryRejected:
        raise
    except RetrievalFailure:
        raise
    except sqlite3.Error as exc:
        raise RetrievalFailure("read-only retrieval failed") from exc
    finally:
        if "connection" in locals():
            connection.close()
