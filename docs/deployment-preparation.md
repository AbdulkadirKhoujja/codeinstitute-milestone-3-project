# Prepared; deployment pending

No cloud resource has been provisioned and no Heroku deployment has been run.
Material verification gaps must be resolved before this becomes a release.

## Configuration decisions

- Keep Django 5.2.17 and Python 3.11; Heroku currently supports 3.11. The
  `.python-version` major/minor declaration receives current patch releases
  on Heroku. Windows verification initially used Python 3.11.0; that old patch
  is not the intended hosted runtime. Ubuntu verification uses Python 3.14.4
  as a supplementary compatibility run, not production-parity evidence.
- Gunicorn supplies the WSGI server, with two initial workers and a 20-second
  worker timeout below Heroku's 30-second router timeout. Confirm resource
  usage and tune worker count for the selected plan before public traffic.
- WhiteNoise serves collected original CSS/JavaScript and Django Admin assets.
  Compressed storage preserves stable filenames and uses normal HTTP caching
  rather than long-lived immutable fingerprints. This small site's static
  cache is deliberately short; fingerprinted storage is a future optimisation.
- Settings are centralised in `byteboard/settings.py`. Export a random secret,
  `DEBUG=false`, explicit `ALLOWED_HOSTS`, and HTTPS `CSRF_TRUSTED_ORIGINS`.
  Never commit real values. `.env.example` contains placeholders and is not
  automatically loaded. Local `env.py` remains ignored.
- Enable `TRUST_HEROKU_PROXY=true` only on Heroku, whose router sets the
  `X-Forwarded-Proto` header. Direct local HTTP must not trust this header.
  Enable `SECURE_SSL_REDIRECT=true` and `DATABASE_SSL_REQUIRE=true` on Heroku.
  Cookies are secure when debug is off. HSTS stays disabled until domain/HTTPS
  verification establishes a safe policy; no preload is requested.

## Separate deployment operation

The owner must supply the Heroku account, app name, region, approved plan,
PostgreSQL resource and final hostname. Creating any billable resources requires
separate approval. Do not use the disposable local test database for production.

After release blockers are resolved:

1. Select the supported Python buildpack for the app. The nested Node package
   is verification-only; it is not needed to run ByteBoard in production.
2. Configure the environment values above through Heroku's protected settings.
   Obtain `DATABASE_URL` from the separately provisioned PostgreSQL resource.
3. Deploy the reviewed commit using the chosen Heroku Git/GitHub workflow.
   The Python build runs `collectstatic`; do not disable that build step.
4. Run `heroku run python manage.py migrate --app <app-name>` and the final
   cache-setup command documented after shared-cache implementation.
5. Create an authorised moderator with `createsuperuser`, entering credentials
   interactively. Do not upload sample community records as real activity.
6. Run production checks, verify all collected assets and custom error pages,
   then execute public/member/moderator workflows over the final HTTPS URL.
7. Check database integrity, cold/warm feed timing, cross-process refresh
   control, logs and development/production parity on the actual host.
8. Record the live URL, tested commit, results and genuine screenshots. Only
   then update deployment-dependent assessment rows.

For local static preparation run `python manage.py collectstatic --noinput`.
For a production-settings check use `python manage.py check --deploy` with
representative configuration. A local Gunicorn command can bind
`127.0.0.1:8001`; never use `runserver` as the production server.

## Observed local preparation

On 8 September 2026 the static-settings regression first failed because
`STATIC_ROOT` was absent. After configuration, 15 settings/error tests passed.
`collectstatic --noinput` copied and post-processed 130 assets. `pip check`
reported no dependency conflicts. Production-oriented Django checks with
explicit hosts, debug off, SSL redirect and proxy trust reported only
`security.W004`: HSTS is deliberately pending final-domain HTTPS verification.
This is local evidence, not a hosted static or deployment pass.

## Official references consulted on 8 September 2026

- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Heroku Python support](https://devcenter.heroku.com/articles/python-support)
- [Runtime declaration](https://devcenter.heroku.com/articles/python-runtimes)
- [Heroku Django configuration](https://devcenter.heroku.com/articles/django-app-configuration)
- [Heroku request timeout](https://devcenter.heroku.com/articles/request-timeout)
- [Heroku routing headers](https://devcenter.heroku.com/articles/http-routing#heroku-headers)
- [WhiteNoise Django integration](https://whitenoise.readthedocs.io/en/stable/django.html)
