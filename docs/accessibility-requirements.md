# Accessibility Requirements

ByteBoard treats accessibility as an implementation requirement throughout development, not a final visual check. The target is a robust experience aligned with WCAG 2.2 Level AA where applicable. Conformance is not claimed before the formal Phase 4 evaluation.

## Phase 2 implementation status

The core interface now provides semantic page landmarks, one primary heading per page, a skip link, native keyboard-operable controls, visible focus styling, mobile-first reflow, and reduced-motion handling. Navigation exposes account state in text, selected category links use `aria-current`, external story links include a new-tab announcement, and dates use machine-readable `time` elements.

Registration, login, and story forms use persistent labels and autocomplete where relevant. Story fields have task-specific instructions. Invalid controls expose `aria-invalid` through Django and reference both their help text and field error; submitted non-sensitive values remain present after validation. Success messages use a live status region, while destructive actions identify the affected story and require an explicit POST confirmation.

No content image is used in Phase 2, so image alternative-text requirements are not yet exercised. Comments and voting controls are Phase 3 work. Contrast measurement, keyboard journey recording, screen-reader spot checks, zoom/reflow evidence, markup/style validation, and cross-browser checks remain Phase 4 tasks; their absence prevents a conformance claim at this point.

## Structure and navigation

- Use semantic HTML landmarks for header, navigation, main content, complementary content, and footer.
- Provide one descriptive main heading per page and a logical heading hierarchy beneath it.
- Include a keyboard-accessible skip link to the main content.
- Identify the current page, selected category, or active filter in text and with appropriate semantics.
- Keep navigation labels and ordering consistent between pages and responsive states.
- Use descriptive link text; identify external article links without relying on an icon alone.

## Keyboard and focus

- Every interactive control must be operable with a keyboard alone.
- Focus order must follow the visual and reading order.
- Focus indicators must remain clearly visible and must not be obscured by sticky content.
- Menus, dialogs, and confirmation flows must manage focus predictably.
- No essential interaction may depend on hover, drag, or a precise pointer gesture.
- Touch targets should be comfortably sized and separated at mobile widths.

## Forms, authentication, and errors

- Associate every form control with a persistent visible label.
- Explain required fields in text and expose the required state programmatically.
- Connect field-level errors and supporting instructions to the corresponding input.
- Provide an error summary for longer forms and move focus appropriately after an invalid submission.
- Preserve valid, non-sensitive values after validation errors.
- Use appropriate autocomplete tokens for registration and sign-in fields.
- Do not reveal whether a particular account exists through authentication error wording.

## Content and media

- Write concise titles, summaries, instructions, and error messages in plain language.
- Provide meaningful alternative text for informative images.
- Use empty alternative text for decorative images that add no information.
- Give diagrams and complex planning images a nearby text explanation where their content is not already represented in the page.
- Do not encode meaning through colour, position, shape, or icons alone.
- Display dates and vote states consistently and with enough surrounding context.

## Visual presentation

- Verify text and essential graphical contrast against WCAG AA thresholds during styling.
- Support browser zoom and text resizing without clipping, overlap, or loss of content.
- Reflow content at narrow widths without two-dimensional scrolling, except where a genuinely two-dimensional component requires it.
- Avoid fixed heights for user-generated titles, summaries, comments, and validation messages.
- Respect user preferences such as reduced motion if animation is introduced later.
- Keep reading columns at a comfortable line length.

## Dynamic feedback

- Ensure success, error, moderation, vote, and deletion feedback is perceivable by screen-reader users.
- Do not move focus unexpectedly after voting or submitting content.
- Label vote controls with both action and current state; a numeric score alone is insufficient.
- Confirm destructive actions using explicit post or comment context.
- Make empty, loading, not-found, and permission-denied states understandable without visual cues alone.

## Responsive requirements

- Begin with a usable single-column layout and enhance it at wider breakpoints.
- Allow metadata and action groups to wrap or stack without changing their meaning.
- Replace wide data rows with labelled stacked values on small screens when necessary.
- Keep primary navigation, search, account state, and the main task reachable in mobile layouts.
- Test common portrait and landscape widths as well as zoomed desktop layouts.

## Testing intentions

Testing in Phase 4 will include:

- keyboard-only journeys for browsing, authentication, posting, commenting, voting, and ownership actions;
- screen-reader spot checks for page structure, forms, feedback, and stateful controls;
- automated accessibility scans as supporting evidence, not a substitute for manual testing;
- colour-contrast measurement after the visual palette is implemented;
- browser zoom, text resize, and responsive reflow checks;
- validation of rendered HTML and CSS where suitable; and
- issue documentation with the tool, page, date, result, and any remediation.

Wireframe SVGs in this repository include accessible titles and descriptions because they are planning artefacts. Their grey palette and placeholder content do not define the final product's colour or typography.
