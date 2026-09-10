from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.db import connection
from django.test import TestCase

from news.models import Comment, Post, Vote


class SampleDataTests(TestCase):
    def test_unreserved_database_is_rejected_before_writing(self):
        with patch.dict(
            connection.settings_dict, {"NAME": "personal.sqlite3"}
        ):
            with self.assertRaisesMessage(CommandError, "Refusing a database"):
                self.seed(confirm_disposable=True)
        self.assertFalse(Post.objects.exists())

    def seed(self, **options):
        call_command("seed_local_samples", stdout=StringIO(), **options)

    def test_requires_explicit_confirmation(self):
        with self.assertRaisesMessage(CommandError, "--confirm-disposable"):
            self.seed()
        self.assertFalse(Post.objects.exists())

    def test_idempotent_data_covers_moderation_drafts_and_pagination(self):
        self.seed(confirm_disposable=True)
        counts = (Post.objects.count(),
                  Comment.objects.count(), Vote.objects.count())
        self.seed(confirm_disposable=True)
        self.assertEqual(counts, (
            Post.objects.count(),
            Comment.objects.count(),
            Vote.objects.count(),
        ))
        self.assertGreater(Post.objects.filter(status="published").count(), 10)
        self.assertTrue(Post.objects.filter(status="draft").exists())
        approval_states = set(
            Comment.objects.values_list("is_approved", flat=True)
        )
        self.assertEqual(approval_states, {True, False})
        moderator = get_user_model().objects.get(username="sample-moderator")
        self.assertTrue(moderator.has_perm("news.change_comment"))
        self.assertFalse(moderator.is_superuser)
        self.assertFalse(moderator.has_usable_password())
        for post in Post.objects.all():
            post.full_clean()

    def test_existing_unmarked_account_is_preserved_and_aborts(self):
        member = get_user_model().objects.create_user(username="sample-editor")
        with self.assertRaisesMessage(CommandError, "Existing account"):
            self.seed(confirm_disposable=True)
        member.refresh_from_db()
        self.assertEqual(member.first_name, "")
        self.assertFalse(Post.objects.exists())
