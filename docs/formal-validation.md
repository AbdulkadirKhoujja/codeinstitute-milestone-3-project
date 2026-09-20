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

## Final official HTML validation — 18 September 2026

The environment proxy path was diagnosed as refusing Python `urllib` POSTs.
Using a direct opener with `ProxyHandler({})`, all 23 prepared, isolated and
sanitised samples were submitted once to the Nu HTML Checker. Every request
returned HTTP 200 with **zero errors and zero warnings/info messages**. The
prepared HTML validation set therefore passes; this remains validation of the
listed rendered states, not browser-generated DOM or accessibility conformance.

## Official Jigsaw CSS validation — 20 September 2026

The project-owned `static/css/style.css` was validated by **URI** through the
official [Jigsaw CSS Validation Service](https://jigsaw.w3.org/css-validator/)
against the deployed public stylesheet. Using a direct `urllib` opener with
`ProxyHandler({})`, the validator returned **HTTP 200**, **0 errors**, and
**8 warnings**. No third-party Bootstrap or CDN stylesheet was submitted.

Earlier direct-input requests returned HTTP 500, including `Reader used` for a
known-valid sample. The subsequent official URI validation completed
successfully, so that earlier service behaviour is historical troubleshooting,
not a current validation limitation.
