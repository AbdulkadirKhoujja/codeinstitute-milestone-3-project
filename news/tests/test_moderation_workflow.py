from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from news.models import Comment


class ModerationWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_local_samples", confirm_disposable=True,
                     stdout=StringIO())
        cls.moderator = get_user_model().objects.get(
            username="sample-moderator"
        )
        cls.pending = Comment.objects.get(is_approved=False)

    def change_url(self):
        return reverse("admin:news_comment_change", args=[self.pending.pk])

    def test_limited_staff_can_find_approve_and_unpublish_a_comment(self):
        self.client.force_login(self.moderator)
        listing = self.client.get(reverse("admin:news_comment_changelist"),
                                  {"is_approved__exact": "0"})
        self.assertContains(listing, self.pending.author.username)
        self.assertEqual(list(listing.context["cl"].queryset), [self.pending])
        data = {
            "post": self.pending.post_id,
            "author": self.pending.author_id,
            "body": self.pending.body,
            "is_approved": "on",
            "_save": "Save",
        }
        self.assertEqual(self.client.post(
            self.change_url(), data).status_code, 302)
        self.pending.refresh_from_db()
        self.assertTrue(self.pending.is_approved)
        self.client.logout()
        detail = reverse("news:post-detail", args=[self.pending.post_id])
        self.assertContains(self.client.get(detail), self.pending.body)
        self.client.force_login(self.moderator)
        del data["is_approved"]
        self.assertEqual(self.client.post(
            self.change_url(), data).status_code, 302)
        self.client.logout()
        self.assertNotContains(self.client.get(detail), self.pending.body)

    def test_ordinary_member_cannot_enter_or_submit_moderation(self):
        self.client.force_login(self.pending.author)
        self.assertEqual(self.client.get(self.change_url()).status_code, 302)
        self.assertEqual(self.client.post(self.change_url(), {
            "is_approved": "on", "_save": "Save",
        }).status_code, 302)
        self.pending.refresh_from_db()
        self.assertFalse(self.pending.is_approved)

    def test_moderator_delete_requires_confirmation(self):
        self.client.force_login(self.moderator)
        url = reverse("admin:news_comment_delete", args=[self.pending.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Comment.objects.filter(pk=self.pending.pk).exists())
        self.assertEqual(self.client.post(
            url, {"post": "yes"}).status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.pending.pk).exists())
