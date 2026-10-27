# BreathBloom Support Resources

## Approved boundary

BreathBloom uses a fixed **United States national fictional-demo scope**. It does
not request or infer a real user's location or condition. Support content is
static, reviewed application content and is not selected from messages, clicks,
timing, completion, geolocation, a classifier, or model output.

BreathBloom is a coursework prototype. It is not an emergency service, is not
monitored, cannot contact help for the user, and does not diagnose, provide
therapy or medical advice, or determine whether someone is in crisis.

## Approved Support wording

> **Support information — United States demo**
>
> BreathBloom is a coursework prototype for fictional scenarios. It is not an
> emergency service, is not monitored, and cannot contact help for you. This page
> does not use your location or activity to choose resources.
>
> **Emergency assistance**
>
> If there is immediate danger or a medical emergency, call 911 now or go to the
> nearest emergency room.
>
> **Crisis support**
>
> In the United States, call or text 988, or use the 988 Lifeline chat, for crisis
> support.
>
> **Non-emergency treatment information**
>
> FindTreatment.gov lists mental-health and substance-use treatment facilities in
> the United States and its territories. It is not an emergency service.
>
> **About BreathBloom**
>
> BreathBloom does not diagnose, provide therapy or medical advice, detect
> distress, or notify another person.
>
> **Return**

Planned resource controls must display the number or URL as text as well as
providing any supported link:

- **Call 911:** `tel:911`
- **Call 988:** `tel:988`
- **Text 988:** `sms:988`
- **988 Lifeline chat:** `https://chat.988lifeline.org/`
- **FindTreatment.gov:** `https://findtreatment.gov/`

The three purposes must remain visually and semantically separate:

- 911 is for immediate danger or a medical emergency.
- 988 is for crisis support by call, text, or official chat.
- FindTreatment.gov is non-emergency treatment-location information.

## Official sources

Access date for every source: **October 27, 2026**.

| Exact page title | Organization | Direct URL | Purpose | Verification result |
| --- | --- | --- | --- | --- |
| Find Support \| SAMHSA | Substance Abuse and Mental Health Services Administration, U.S. Department of Health and Human Services | https://www.samhsa.gov/find-support | Official starting point for support, including 988 and treatment-information routes | Current official SAMHSA result and service summary confirmed. Automated direct-page retrieval returned an access-control response, so the page must be manually reopened before publication. |
| National 911 Program \| 911.gov | National 911 Program, National Highway Traffic Safety Administration Office of Emergency Medical Services, U.S. Department of Transportation | https://www.911.gov/ | Official federal 911 information and direction to call 911 for an emergency | Direct page opened successfully and identified the maintaining federal program and emergency purpose. |
| 988 Suicide & Crisis Lifeline \| SAMHSA | Substance Abuse and Mental Health Services Administration, U.S. Department of Health and Human Services | https://www.samhsa.gov/mental-health/988 | Official federal information about calling, texting, or chatting with 988 | Current official SAMHSA result and 988 call/text/chat summary confirmed. Automated direct-page retrieval returned an access-control response, so the page must be manually reopened before publication. |
| 988 Lifeline | 988 Suicide & Crisis Lifeline | https://chat.988lifeline.org/ | Official 988 chat entry point | The official `https://988lifeline.org/chat/` entry opened and redirected to this HTTPS chat URL. No chat was started. |
| FindTreatment.gov | SAMHSA Center for Behavioral Health Statistics and Quality | https://findtreatment.gov/ | Non-emergency locator for mental-health and substance-use treatment facilities in the United States and its territories | Direct official page opened successfully. No search or location was submitted. |
| FAQs - FindTreatment.gov | SAMHSA Center for Behavioral Health Statistics and Quality | https://findtreatment.gov/faqs | Explains the locator's scope and limits, including that it does not recommend a facility for an individual situation | Direct official page opened successfully and current FAQ content was confirmed. |
| About - FindTreatment.gov | SAMHSA Center for Behavioral Health Statistics and Quality | https://findtreatment.gov/about | Identifies the responsible SAMHSA program and the locator's purpose | Direct official page opened successfully and the official ownership/purpose page was confirmed. |

These checks verify source identity, URL, and current stated purpose only. They do
not verify application behavior and do not clinically validate BreathBloom.

## Planned route behavior

- Support information remains directly available from entry, setup, loading,
  model failure, deterministic fallback, ready, exercise, paused, stopped,
  completed, interrupted, Next-time setup, and history-question/history states.
- The static wording and displayed numbers must render without FastAPI, SQLite,
  a runtime model/provider, a classifier, geolocation, or a successful network
  request.
- Before or after a practice, **Return** restores the preceding non-exercise view
  without changing it.
- Opening Support during an exercise immediately pauses local timing, freezes the
  current phase offset and completed-cycle count, and attempts an honest pause
  save without making the pause depend on that save.
- During a practice the return control is labeled **Return to paused practice**.
- Returning shows the paused state and never resumes automatically. Only
  **Resume practice** or **Stop** may continue the flow.
- A history question outside the approved factual allow-list receives the neutral
  deterministic scope message and retains a visible Support link. BreathBloom
  does not claim why the question was out of scope or infer the user's condition.

## Manual re-verification procedure

Recheck all resources before each graded submission or demonstration, at least
every 90 days while the project is active, and whenever an official URL redirects
or changes.

1. Open each direct URL in a normal browser without submitting personal data.
2. Confirm the page title, responsible organization, HTTPS URL, and stated
   purpose.
3. Confirm that the displayed 911 and 988 actions and official 988 chat entry are
   current.
4. Confirm that FindTreatment.gov remains non-emergency location information and
   review its FAQ or About page for material scope changes.
5. Record the verifier, verification date, observed redirect, result, and next
   review date in this table or a later verification record.
6. If a source cannot be confirmed, do not describe it as verified or current;
   resolve the source before publishing the Support route.

Automated link checks may supplement but cannot replace manual review. No
resource may be dynamically selected from user data.
