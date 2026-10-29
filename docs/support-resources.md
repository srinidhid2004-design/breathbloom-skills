# FocusBloom Support Resources

## Approved boundary

FocusBloom uses a fixed **United States national fictional-demo scope**. It does
not request or infer a real user's location or condition. Support content is
static, reviewed application content and is not selected from messages, clicks,
timing, completion, geolocation, a classifier, or model output.

FocusBloom is a coursework prototype. It is not an emergency service, is not
monitored, cannot contact help for the user, and does not diagnose, provide
therapy or medical advice, or determine whether someone is in crisis.

## Approved Support wording

> **Support information — United States demo**
>
> FocusBloom is a coursework prototype for fictional scenarios. It is not an
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
> **About FocusBloom**
>
> FocusBloom does not diagnose, provide therapy or medical advice, detect
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

Manual access date for every source: **October 29, 2026**. Verifier: Codex using
a normal browser under the human-authorized publication checkpoint. Next review
due by **January 27, 2027**, or sooner after a redirect or material change.

| Exact page title | Organization | Direct URL | Purpose | Verification result |
| --- | --- | --- | --- | --- |
| Find Support \| SAMHSA | Substance Abuse and Mental Health Services Administration, U.S. Department of Health and Human Services | https://www.samhsa.gov/find-support | Official starting point for support, including 988 and treatment-information routes | Direct HTTPS page opened manually with no redirect. The official U.S. government/SAMHSA identity, support purpose, 988 routes, and treatment-information route were visible. |
| National 911 Program \| 911.gov | National 911 Program, National Highway Traffic Safety Administration Office of Emergency Medical Services, U.S. Department of Transportation | https://www.911.gov/ | Official federal 911 information and direction to call 911 for an emergency | Direct HTTPS page opened manually with no redirect. It identified NHTSA's National 911 Program and stated that emergency assistance is not available through the website and to call 911 immediately. |
| 988 Suicide & Crisis Lifeline \| SAMHSA | Substance Abuse and Mental Health Services Administration, U.S. Department of Health and Human Services | https://www.samhsa.gov/mental-health/988 | Official federal information about calling, texting, or chatting with 988 | Direct HTTPS page opened manually with no redirect. The official SAMHSA/HHS identity and 24/7 call, text, and chat purpose were visible. |
| 988 Lifeline Pre Conversation Survey | 988 Suicide & Crisis Lifeline, with SAMHSA and Vibrant Emotional Health identified in the footer | https://chat.988lifeline.org/ | Official 988 chat entry point | Direct HTTPS destination opened manually. The official `https://988lifeline.org/chat/` entry redirected to this URL. The survey and Start a Chat control were visible, but no cookie choice, field, or chat was submitted. |
| Home - FindTreatment.gov | SAMHSA Center for Behavioral Health Statistics and Quality, U.S. Department of Health and Human Services | https://findtreatment.gov/ | Non-emergency locator for mental-health and substance-use treatment facilities in the United States and its territories | Direct HTTPS page opened manually with no redirect. Official HHS/SAMHSA identity and locator purpose were visible; no search or location was submitted. |
| FAQs - FindTreatment.gov | SAMHSA Center for Behavioral Health Statistics and Quality, U.S. Department of Health and Human Services | https://findtreatment.gov/faqs | Explains the locator's scope and limits, including that it does not recommend a facility for an individual situation | Direct HTTPS page opened manually with no redirect. It confirmed that the resource cannot recommend or endorse an individual facility or treatment type. |
| About - FindTreatment.gov | SAMHSA Center for Behavioral Health Statistics and Quality, U.S. Department of Health and Human Services | https://findtreatment.gov/about | Identifies the responsible SAMHSA program and the locator's purpose | Direct HTTPS page opened manually with no redirect. It identified CBHSQ/SAMHSA ownership, locator purpose, and the non-referral/non-endorsement limitation. |

These checks verify source identity, URL, and current stated purpose only. They do
not verify application behavior and do not clinically validate FocusBloom.
The categories remained distinct: 911 for immediate danger or medical emergency,
988 for crisis support, and FindTreatment.gov for non-emergency treatment-location
information. No call, text, chat, search, location, or personal-data submission
occurred during the review.

## Implemented route behavior

- Support information remains directly available from entry, every Focus Garden
  state, every Perspective Studio state, Next-Step Seed, every History Garden and
  Garden Guide state, loading, no-match, query-rejected, and model-failed states.
- The static wording and displayed numbers must render without FastAPI, SQLite,
  a runtime model/provider, a classifier, geolocation, or a successful network
  request.
- **Return** restores the preceding view without changing activity, entry, saved
  text, or provider status.
- Opening Support during an active Focus Garden activity suspends local work and
  clears pending timers/callbacks without making Support depend on a save.
- During an activity, returning restores the explicitly suspended/stopped view;
  no activity or request resumes automatically. Any resumable-activity behavior
  must be separately decided and verified before implementation.
- A history question outside the approved factual allow-list receives the neutral
  deterministic scope message and retains a visible Support link. FocusBloom
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
