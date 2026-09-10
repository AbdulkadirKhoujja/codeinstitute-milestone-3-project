# Comment moderation verification

On 10 September 2026, Django-client journeys exercised the existing Admin with
a staff member holding only comment view, change and delete permissions.

| Journey | Expected and actual result |
| --- | --- |
| Find pending comments | Approval filter lists the pending sample and its author |
| Approve | Staff saves approval; an anonymous detail request displays the comment |
| Unpublish/reject from public view | Staff clears approval; anonymous detail hides it |
| Delete unwanted content | GET displays confirmation without deletion; confirmed POST removes it |
| Ordinary member attempts moderation | Admin redirects to login; approval remains unchanged |
| Author edits approved content | Existing update tests confirm it returns to pending |

The existing Admin is sufficient for this workflow; no custom moderation app
or additional staff permissions were needed. Clearing approval retains a
private pending record; deletion removes it. These are different operations.
Admin and new moderation-workflow checks: **11 tests passed in 1.624 seconds**.
This audits existing behaviour, not a retrospective TDD claim.

A new test found that the comment edit page did not explain the moderation
consequence before submission. It failed before a plain-language warning was
added. Update, ownership and visibility regressions then passed **15 tests in
13.030 seconds**. The warning does not change the existing moderation policy.

These are actual HTTP/view/database tests using isolated sample records, not
manual browser sessions. Keyboard, visual layout and staff browser journeys
still require a connected browser.
