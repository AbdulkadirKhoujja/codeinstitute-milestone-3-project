# Disposable local sample data

`seed_local_samples` is opt-in and refuses ordinary personal/production database
names. It accepts only the reserved `byteboard-phase4.sqlite3`, PostgreSQL
`byteboard_phase4`, or isolated test/in-memory databases. Always select the
disposable database before migrating or running the command.

```powershell
$env:DEBUG = 'true'
$env:SQLITE_PATH = 'C:\path\to\byteboard-phase4.sqlite3'
python manage.py migrate
python manage.py seed_local_samples --confirm-disposable
python manage.py changepassword sample-editor
python manage.py changepassword sample-reader
python manage.py changepassword sample-moderator
python manage.py runserver 127.0.0.1:8000
```

Enter local-only passwords interactively. An optional `BYTEBOARD_SAMPLE_PASSWORD`
environment value is used only for newly created sample accounts; otherwise
their passwords are unusable until `changepassword` is run. No credential is
printed, committed or reset on a repeated seed. Do not reuse a real password.

There are 14 published stories, two drafts including a long title, four
categories including an empty one, approved/pending comments and positive/
negative totals. All stories are explicitly labelled fictional samples, use
`example.com` source links and contain original discussion exercises. Two
ordinary members own records; the staff moderator has only comment view,
change and delete permissions, not superuser rights.

The command is transactional and idempotent for unchanged sample records. It
refuses unmarked account/category collisions and preserves existing values.
Four tests cover opt-in, database guard, collision rollback, repeatability,
field validity and the required sample states. They passed in 0.766 seconds
after an initial missing-command failure. This prepares browser data; it does
not establish that browser journeys have been executed.
