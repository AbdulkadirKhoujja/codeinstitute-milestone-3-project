"""Load the authoritative settings with isolated, placeholder configuration."""

import os
import runpy
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase


class ReleaseSettingsTests(SimpleTestCase):
    def load_settings(self, **environment):
        with patch.dict(os.environ, environment, clear=True):
            with patch("os.path.isfile", return_value=False):
                return runpy.run_path(settings.BASE_DIR / "byteboard/settings.py")

    def test_debug_defaults_off_and_cookies_default_secure(self):
        config = self.load_settings(SECRET_KEY="test-only-placeholder")
        self.assertIs(config["DEBUG"], False)
        self.assertTrue(config["SESSION_COOKIE_SECURE"])
        self.assertTrue(config["CSRF_COOKIE_SECURE"])
        self.assertEqual(config["ALLOWED_HOSTS"], [])

    def test_explicit_local_configuration_and_host_parsing(self):
        config = self.load_settings(
            SECRET_KEY="test-only-placeholder", DEBUG="true",
            ALLOWED_HOSTS="localhost, 127.0.0.1,",
        )
        self.assertTrue(config["DEBUG"])
        self.assertFalse(config["SESSION_COOKIE_SECURE"])
        self.assertEqual(config["ALLOWED_HOSTS"], ["localhost", "127.0.0.1"])

    def test_invalid_boolean_does_not_silently_enable_debug(self):
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings(SECRET_KEY="test-only-placeholder", DEBUG="maybe")

    def test_missing_secret_fails_without_exposing_configuration(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "SECRET_KEY"):
            self.load_settings()

    def test_proxy_headers_require_explicit_heroku_opt_in(self):
        config = self.load_settings(SECRET_KEY="test-only-placeholder")
        self.assertIsNone(config["SECURE_PROXY_SSL_HEADER"])
        config = self.load_settings(
            SECRET_KEY="test-only-placeholder", TRUST_HEROKU_PROXY="true",
            SECURE_SSL_REDIRECT="true",
            CSRF_TRUSTED_ORIGINS="https://byteboard.example",
        )
        self.assertEqual(config["SECURE_PROXY_SSL_HEADER"], (
            "HTTP_X_FORWARDED_PROTO", "https",
        ))
        self.assertTrue(config["SECURE_SSL_REDIRECT"])
        self.assertEqual(config["CSRF_TRUSTED_ORIGINS"], [
            "https://byteboard.example",
        ])
        self.assertEqual(config["SECURE_HSTS_SECONDS"], 0)

    def test_postgresql_url_is_parsed_in_authoritative_settings(self):
        config = self.load_settings(
            SECRET_KEY="test-only-placeholder",
            DATABASE_URL="postgresql://member:placeholder@localhost:5432/byteboard",
        )
        database = config["DATABASES"]["default"]
        self.assertEqual(database["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(database["NAME"], "byteboard")
        self.assertEqual(database["HOST"], "localhost")
        self.assertEqual(database["OPTIONS"]["connect_timeout"], 5)

    def test_sqlite_path_can_target_disposable_local_data(self):
        config = self.load_settings(
            SECRET_KEY="test-only-placeholder", SQLITE_PATH="sample.sqlite3",
        )
        self.assertEqual(str(config["DATABASES"]["default"]["NAME"]),
                         "sample.sqlite3")

    def test_database_url_errors_do_not_echo_credentials(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured, "DATABASE_URL must be a PostgreSQL URL",
        ):
            self.load_settings(
                SECRET_KEY="test-only-placeholder",
                DATABASE_URL="unknown://member:private-placeholder@host/database",
            )
