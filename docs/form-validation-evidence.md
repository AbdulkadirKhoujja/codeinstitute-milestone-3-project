# Rendered form error associations

On 8 September 2026, two rendered-response tests reproduced defects:

- Submitting an empty login form generated `aria-describedby` references to
  `id_username_error` and `id_password_error`, but neither ID existed.
- Submitting a short numeric registration password generated three elements
  with the same `password2-error` ID.

The login error container now uses Django's generated field ID. Registration
places all errors for one field inside a single labelled container. The tests
parse actual response HTML, require every description target to exist exactly
once, and reject duplicate IDs. Both failed before the template corrections.

After correction, `python manage.py test accounts --noinput` passed all 20
tests in 24.413 seconds on SQLite. These are markup association checks, not
screen-reader, keyboard or browser accessibility evidence.
