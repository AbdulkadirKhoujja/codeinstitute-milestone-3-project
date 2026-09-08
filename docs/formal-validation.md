# Formal front-end validation

## Official W3C HTML check — 8 September 2026

Service: [Nu HTML Checker](https://validator.w3.org/nu/), version **26.9.7**.
Run `python verification/official_validation.py` for a no-upload dry run.
`--upload` requires explicit approval to send source to the external service.

The script creates an isolated in-memory database, seeds only labelled fictional
records, and renders Django responses. It never reads the ordinary local
database. CSRF inputs and password values are removed before submission;
password fields remain so their labels can still be validated. Session cookies,
headers, credentials and private records are not uploaded. A regression test
first exposed an over-aggressive sanitiser removing the password label target;
the corrected sanitiser passed alongside account markup checks.

The initial official run found excessive fractional-second precision in `time`
attributes and `aria-label` on generic action divs. It also warned that comment
articles lacked identifying headings. Rendered-response tests reproduced these
problems before correction. Timestamps now use second precision with a timezone
offset, action containers have `role="group"`, and comment author links sit in
headings. A test was corrected to accept the intentionally date-only profile
join date; that was a test expectation issue, not an application defect.

After correction, **all 23 samples returned zero errors and zero warnings**:

| Scope | Samples |
| --- | --- |
| Public discovery | Empty home, populated home, page two, discovery, empty category |
| Story detail | Anonymous and signed-in member |
| Authentication | Login, registration, required login errors, multiple password errors |
| Member records | New/edit/delete story, owner profile, invalid story form |
| Discussion | Edit/delete comment, invalid comment form |
| Errors | 400, 403, 404, 500 |

The related rendered-markup, detail, comment visibility, profile and account
markup regression group passed **22 tests in 9.974 seconds** on SQLite.
Validation applies to these rendered states, not every possible user input,
browser-generated DOM state or third-party administration screen. It does not
establish accessibility conformance or browser behaviour.

## Official Jigsaw CSS check — unresolved

The custom `static/css/style.css` was submitted to the official
[Jigsaw service](https://jigsaw.w3.org/css-validator/validator), following its
[documented API](https://jigsaw.w3.org/css-validator/manual.html). Direct-input
POSTs using CSS3/SOAP and CSS3/text responses returned **HTTP 500**. A separate
documented URL-validation request for the already-public committed stylesheet
also returned HTTP 500. No useful CSS diagnostics or official pass were obtained.
No third-party Bootstrap CSS is represented as original project CSS.

Retry `python verification/official_validation.py --css --upload` with approval
when the service is available, correct any genuine findings and retain the
result for the final stylesheet. CSS formal validation remains an explicit gap.
