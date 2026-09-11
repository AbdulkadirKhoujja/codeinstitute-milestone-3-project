# Manual browser verification — 11 September 2026

## Environment and scope

Executed against the local application, beginning at `2e82528`, using the
Codex In-app Browser (Chromium-based; engine version was not captured).
Desktop 1440 × 900, tablet 768 × 1024 and mobile 390 × 844 viewport presets
were used. These are emulated viewport sizes, not physical device tests.
The runtime served `127.0.0.1:8000` with Django's development server.

The existing guarded `seed_local_samples --confirm-disposable` workflow was
used with the ignored `verification/browser-session/byteboard-phase4.sqlite3`
database. It supplied 14 published stories, two drafts, four categories,
approved/pending comments and restricted moderator permissions. Disposable
accounts and fictional browser samples were used; no production or ordinary
local database was selected. No credentials are recorded here.

Private local configuration was bypassed. DEBUG was false to exercise custom
errors; cookie secure flags were disabled in the local process for HTTP, and
runserver's insecure static option was requested. The resumed check found that manifest URLs still referenced collected CSS; source-asset retests used the isolated override described below. This is not hosted,
HTTPS, collected-static or production-parity evidence.

## Journey record

Evidence references below describe browser snapshots, observed interactions
and read-only DOM measurements from this execution session. They are a durable
written record, not exported browser traces. Screenshots were displayed in the
session only; no screenshot image files were saved or committed.

| ID / journey | Viewport | Expected | Actual / evidence | Result |
| --- | --- | --- | --- | --- |
| B01 Home and pagination | Desktop | Published feed; next page works | Ten cards on page 1, four on page 2; meaningful titles, metadata and navigation in browser snapshot | Pass |
| B02 Search and empty results | Desktop/mobile | Matching results and useful no-match state | Dependency search returned the matching sample; unmatched query displayed guidance and clear-filter action | Pass |
| B03 Categories and sorting | Desktop | Category filter and highest-rated order | Highest-rated sample led with score 2; empty category displayed its empty state and retained sort selection | Pass for these cases; oldest/title orders not exercised |
| B04 Registration | Mobile | Invalid fields explain errors; valid account can join | Required-field and password-similarity errors observed; corrected disposable registration succeeded and signed in | Pass |
| B05 Login/logout | Mobile/tablet | Login validates and returns to requested page; logout ends session | Anonymous submission redirected to login; empty login errors appeared; valid login returned to submission; logout showed anonymous navigation | Pass |
| B06 Owner/public profiles and drafts | Mobile/tablet | Draft visible only to owner; public profile excludes it | Owner saw private draft and controls; anonymous profile omitted draft section and direct draft URL gave custom 404 | Pass, with D1 corrected below |
| B07 Story creation/publication/edit | Mobile/tablet | Validate, save draft, retain edit values and publish | Required errors observed; draft created; edit prepopulated; published update became anonymously readable | Pass, with D2 corrected below |
| B08 Story deletion | Tablet | Confirmation permits cancellation, then authorized deletion | Keep story returned to intact item; confirmed deletion succeeded; original URL returned custom 404 | Pass |
| B09 Comment lifecycle | Tablet | Validate; pending until moderated; author can edit/delete | Empty error; new pending comment; pending edit; after approval, author edit returned it to pending; confirmed deletion removed it | Pass |
| B10 Moderation | Tablet | Pending hidden publicly; restricted staff can approve | Anonymous view omitted pending comment; staff admin exposed Comments; approval reduced pending filter from two to one; approved comment became public | Pass |
| B11 Authorization | Tablet | Non-owner cannot edit another user's records; nonstaff cannot access admin | Non-owner story/comment edit URLs returned custom 404; ordinary member received admin login denial | Pass for exercised boundaries |
| B12 JavaScript votes | Tablet | Add, reverse and remove vote without navigation | Upvote reached +1 with pressed state/status; downvote changed to -1; repeated downvote removed vote to 0; public view later showed updated score | Pass |
| B13 Discovery | Tablet/mobile | Loading feedback, then external results; refresh works | Loading text and disabled refresh observed; 30 actual upstream stories rendered; refresh returned results; warning/error console query empty | Pass for loading/success/refresh; outage paths not exercised |
| B14 Expired form session | Mobile | CSRF rejection has useful safe recovery | Login in another tab rotated token; submitting old login form rendered custom 403 with session-expired explanation and home link | Pass |
| B15 Custom 404 | Mobile/tablet | Unavailable/private/deleted record fails safely | Custom 404 observed for draft, unauthorized edits and deleted story | Pass |

Temporary story 17 and comment 3 were deleted through the UI as part of the
lifecycle checks. A second fictional draft (18) remains only in the disposable
database for the D1 retest. Seeded and temporary data are not release data.

## Responsive and accessibility observations

| ID / check | Coverage | Expected | Actual / evidence | Result |
| --- | --- | --- | --- | --- |
| R01 Mobile navigation | 390 × 844 | Menu can expose all member actions | Open navigation expanded to expose member links and logout | Pass |
| R02 Layout/usability | Desktop, tablet, mobile | Readable content and usable forms without observed overlap | Feed, profile, story/comment forms and discovery were used across the listed sizes; normal tablet/mobile discovery screenshots showed readable cards | Pass for sampled views, not every route at every size |
| R03 Horizontal overflow | Mobile discovery and story detail | Document width does not exceed viewport content width | Read-only DOM measurements: clientWidth 375 and scrollWidth 375 on both views | Pass for measured views |
| A01 Keyboard search | Mobile | Skip link and search operable without pointer | Tab focused skip link; Return focused main; Tab reached search; typing, Tab and Return submitted correct search | Pass |
| A02 Visible focus/tab order | Mobile | Focus visible and follows form order | Skip link had visible 3px outline; story Title to Summary followed expected order | Pass for sampled controls only |
| A03 Control dimensions | Mobile story detail | Controls remain usable | Navigation 56 × 40; upvote 88 × 44; downvote 98 × 44; add-comment about 133 × 38 CSS pixels | Observation; no blanket target-size conformance claim |
| A04 Validation recovery | Browser after fix | Error summary receives focus and links reach fields | Invalid story submission focused error-summary; selecting Title error moved focus to id_title | Pass after D2 fix |

Useful session-only screenshots showed tablet discovery, mobile discovery and
mobile custom 403. Initial resize captures that were stale/squashed were not
accepted as evidence. No screen reader was used. Readability observations are
not measured contrast results or an accessibility conformance claim.

## Defects and retests

| Defect | Reproduction / cause | Fix and evidence |
| --- | --- | --- |
| D1 Misleading owner empty state | Owner with a private draft was told they had not submitted any stories; wording did not distinguish publication | Profile now says no stories have been published. Browser retest with draft 18 showed correct text alongside the private draft. |
| D2 Story errors lacked focused summary | Empty story submission showed inline errors but left focus on BODY with no error summary | Shared create/edit template now has an autofocus, programmatically focusable error summary with field links. Browser confirmed summary focus and Title link focus; inline errors retained. |

Fix commit: `88be9ba` — `fix: clarify draft profiles and focus story validation errors`.
Nineteen focused Django tests passed across profiles, story create/update and
rendered markup; system check found no issues. Python style checks for changed
test files and git whitespace check passed. No JavaScript or model changes.
The earlier 209-test/8-JavaScript-test baseline was not rerun wholesale.
Existing regression tests were extended; the total test count did not increase.

## Historical interruption and remaining gaps at d3ed877

Browser control subsequently timed out repeatedly, including the connection
inventory. A final 320px reflow attempt was interrupted and is **not a pass**.
Further interactive work requires a working browser connection.

- Complete 320px and browser zoom/reflow checks, full keyboard journeys and
  mobile landscape coverage; inspect remaining page layouts at each size.
- Exercise oldest/title sorting, populated-category combinations, remaining
  authorization cases and discovery failure/stale/empty recovery states.
- Verify voting with JavaScript disabled in a browser that supports that
  setting; ordinary form fallback was not manually exercised.
- Safely exercise 400 if a suitable local browser path is established; 403 and
  404 were checked, but do not imply every error handler was browser-tested.
- Capture selected screenshots as durable assessment artifacts, record browser
  version, and check other supported browsers/physical devices.
- Screen-reader checks, measured contrast, fuller focus/tab-order inspection,
  network inspection and performance evidence remain outstanding.
- Revalidate changed story-form HTML; earlier HTML validation predates this fix.
  CSS validation remains unresolved after the previously recorded HTTP 500.
- Full PostgreSQL suite, hosted-runtime/HTTPS/static/migration checks and final
  release evidence remain outstanding. No deployment or live URL is recorded.

Next task: restore browser control and finish the interrupted narrow/zoom and
keyboard checks, then the unchecked journey variants above. Do not restart the
completed CRUD/authentication/moderation block without a regression reason.

## Resumed execution — 11 September 2026

Browser recovery succeeded after resetting the connection and opening a fresh
local tab. One later timeout was also recovered with a fresh tab. No accepted
baseline audit or full application test suite was repeated.

For CSS retests, a local process on port 8001 used the same guarded disposable
database and `StaticFilesStorage` instead of manifest storage. This ensured
that the browser loaded changed source CSS rather than the earlier collected
asset. Production settings and collected assets were not changed.

Two additional loopback-only WSGI wrappers used the same disposable database:
port 8002 added `Content-Security-Policy: script-src 'none'`; port 8003 used an
in-process replacement for `news.views.get_top_stories` which waited two
seconds, raised `ExternalFeedError` on its first request, then returned an empty
list. Application views and frontend code handled those states normally.
These process-only fixtures were not committed or applied to production.
They establish frontend/form behaviour, not an actual upstream outage or
complete browser-native JavaScript-disabled behaviour (including noscript).

| ID / check | Browser / viewport | Expected | Actual and evidence | Result |
| --- | --- | --- | --- | --- |
| R04 Narrow home/category navigation | In-app browser, 320 × 800 | Categories reflow without sideways scrolling | Initially links extended to x=711 beyond 305px content area inside a horizontal scroller; after D3 every link ended within x=255 and wrapped to new rows; document client/scroll widths both 305 | Pass after fix |
| R05 Narrow story validation/detail | In-app browser, 320 × 800 | Text and controls fit; validation focus remains useful | Invalid story summary readable and focused; document client/scroll widths both 305; draft detail also 305/305 | Pass for sampled views |
| R06 Desktop category regression | In-app browser, 1280 × 900 | Categories remain a usable row where space permits | All five links shared the same vertical position; document client/scroll widths both 1265 | Pass |
| R07 Landscape discovery | In-app browser, 667 × 375 | Empty discovery state remains within width | Document client/scroll widths both 652 | Pass for measured width; not all landscape pages |
| A05 Navigation and story-form keyboard sequence | In-app browser, 320 × 800 | Menu and form reachable in logical order | Tab reached collapsed menu; Return expanded it; subsequent Tabs reached Home, Discover, Submit; form sequence was Title, Summary, URL, content, category, status, submit, cancel; Shift+Tab/Return submitted invalid form and focused summary | Pass |
| A06 Ownership keyboard path | In-app browser, 320 × 800 | Draft actions and safe cancellation operable | From skip link: submit-new, draft title, edit, delete; Return opened confirmation; keyboard reached Keep story and returned to intact draft | Pass |
| A07 Account keyboard path | In-app browser, desktop | Login fields and submission operable without pointer | Logout and login links activated with Enter; username, Tab, password, Tab, Enter signed in and showed welcome message | Pass |
| A08 Keyboard sorting | In-app browser, desktop | Native sort select and Apply work | End selected title order; Tab/Enter applied correctly alphabetized results; ArrowUp selected oldest and Apply showed earliest samples first | Pass |
| F01 Script-blocked voting | In-app browser, 1280 × 900, port 8002 | Ordinary POST/redirect supports add/reverse/remove | Enter activated Upvote: score 2 to 3 with server success message; Downvote: 3 to 1; repeat Downvote: 1 to 2; final URL ended in #rating-heading | Pass for application-script-blocked fallback |
| F02 Script-blocked validation | Same | Empty comment gives server error without scripts | Enter on Add comment returned required-field error while preserving existing discussion | Pass |
| F03 Discovery failure/retry/empty | In-app browser, desktop, port 8003 | Loading disables refresh; failure offers retry; empty success recovers | Loading and disabled refresh observed; simulated 503 produced unavailable/try-again message; Enter on refresh showed loading then No external stories are available right now; button re-enabled | Pass for controlled fixtures |
| A09 Measured text contrast | Rendered story-form styles | Normal text reaches 4.5:1 | Summary link initially 4.19:1; corrected link 10.22:1. Help text 5.81:1, inline error 9.19:1, submit label 5.59:1 | Pass for listed pairs after D4 fix |
| A12 Comment keyboard lifecycle | In-app browser, desktop | Comment create/edit/delete works through keyboard controls | Typed disposable comment, Tab/Enter submitted pending comment; Enter opened edit, keyboard appended text and submitted; deletion confirmation displayed edited body and Delete comment was activated with Enter | Exercised; no screen-reader announcement claim |
| A13 Registration keyboard order | In-app browser, desktop | Fields and actions follow reading order | Focus started on username; Tab sequence password, confirmation, Create account, Cancel, login link | Pass for tab order; account creation was already tested in the initial block |
| A10 Browser zoom | In-app browser, 1280 × 900 | Zoom changes effective CSS viewport and content reflows | Four Ctrl+plus attempts left measured innerWidth at 1280; no zoom percentage could be verified; Ctrl+0 sent afterward | Unverified; viewport emulation is not zoom evidence |
| A11 Screen reader | Available browser-control environment | Genuine assistive-technology interaction | No screen-reader interface or native app control available; accessibility tree inspection is not a screen-reader test | Not performed |
| E01 Persistent screenshots | In-app browser | Save useful screenshot artifacts | Before/after 320px screenshots displayed in session; documented content export returned unsupported; screenshot API exposes bytes/display without a documented repository-save operation | No persistent image files saved |

Contrast ratios used the rendered foreground/background RGB values and the
sRGB relative-luminance formula `(Llighter + 0.05)/(Ldarker + 0.05)`. Summary
background was (248,215,218); links changed from (8,117,104) to inherited
(88,21,28). Help text was (84,104,117) on white; inline error (123,32,23) on
(255,240,238); submit text white on (8,117,104). Browser retest confirmed the
new computed summary link colour, retained focus and narrow reflow. This is
sampled contrast evidence, not a whole-site contrast or WCAG conformance pass.

### Additional corrections

- D3: Removed horizontal scrolling/max-content sizing from category navigation
  and enabled flex wrapping, as required by the documented narrow reflow goal.
- D4: Error-summary links now inherit the dark alert text colour, including
  interactive states, rather than using insufficient-contrast global teal.

Both CSS-only corrections were browser-retested and pushed in `3bb151a` —
`fix: wrap narrow category navigation and improve error contrast`.
The diff and whitespace checks passed. No Python, JavaScript, template or
schema code changed in this block, so no Django suite rerun was warranted.
Viewport overrides were reset after testing.

### Generated external-link accessibility retest

The initial browser check after `e974256` failed because the controlled fixture
served a stale cached `external-feed.js` response: neither generated link had
an `aria-label`. A fresh fixture on a new local origin loaded the corrected
implementation. Its browser accessibility tree exposed the story link as
`[Browser sample] Fresh discovery result (opens in a new tab)` and the
discussion link as `View discussion (2 comments) (opens in a new tab)`.
The final browser accessibility-tree retest passed for both generated links.

### Zoom/reflow closure

Genuine browser zoom/reflow was attempted, but the available controlled browser
does not expose measurable zoom: Ctrl+plus left the CSS viewport unchanged.
Zoom/reflow therefore remains **blocked by the verification environment**. It
is neither a pass nor an application failure. All other targeted browser checks
in this record are complete.

### Current remaining verification gaps

This section supersedes the historical interruption list above.

- Use a browser with working zoom controls for genuine zoom/text resizing and
  native JavaScript-disabled navigation/noscript verification. Script-blocked
  voting and comment-form fallback are now evidenced separately above.
- Complete broader focus-state and keyboard coverage beyond the exercised
  journeys, additional landscape layouts and cross-browser/device coverage.
- Screen-reader interaction and broader measured contrast/focus-state coverage
  require suitable assistive-technology/browser controls.
- Save selected screenshots as repository artifacts with a supported capture
  export workflow; current screenshots remain session-only.
- Discovery partial/stale/malformed-response browser variants and safe 400
  coverage remain; controlled outage/loading/retry/empty checks are complete.
- Revalidate changed HTML/CSS. Official CSS service success remains unrecorded.
  Full PostgreSQL, hosted runtime and release/submission checks remain open.

Next Phase 4 task: obtain a browser/session supporting genuine zoom, native
script disabling, assistive technology and persistent screenshot export; then
finish those capability-dependent checks and discovery partial/stale variants.
No deployment, production readiness or accessibility conformance is claimed.
