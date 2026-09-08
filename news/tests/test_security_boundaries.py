from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import DatabaseError
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils.functional import SimpleLazyObject

from news.error_views import server_error
from news.models import Comment, Post, Vote


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class SecurityBoundaryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_local_samples", confirm_disposable=True,
                     stdout=StringIO())
        cls.member = get_user_model().objects.get(username="sample-editor")
        cls.post = Post.objects.get(title__startswith="[Sample] A practical")
        cls.comment = Comment.objects.get(author=cls.member)

    def test_csrf_failure_uses_custom_page_and_does_not_mutate(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        count = Comment.objects.count()
        response = client.post(reverse("news:comment-create", args=[self.post.pk]),
                               {"body": "Rejected request"})
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        self.assertEqual(Comment.objects.count(), count)

    def test_csrf_token_is_required_and_foreign_origin_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        client.get(reverse("news:post-detail", args=[self.post.pk]))
        token = client.cookies["csrftoken"].value
        url = reverse("news:comment-create", args=[self.post.pk])
        data = {"body": "A token-protected sample", "csrfmiddlewaretoken": token}
        response = client.post(url, data, HTTP_ORIGIN="https://untrusted.example")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Comment.objects.filter(body=data["body"]).exists())
        self.assertEqual(client.post(url, data).status_code, 302)
        self.assertTrue(Comment.objects.filter(body=data["body"]).exists())

    def test_server_error_survives_unavailable_lazy_session_user(self):
        def failed_user():
            raise DatabaseError("Private database diagnostic")

        request = RequestFactory().get("/isolated-failure/")
        request.user = SimpleLazyObject(failed_user)
        response = server_error(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Something went wrong", response.content)
        self.assertNotIn(b"Private database diagnostic", response.content)

    def test_get_requests_do_not_change_comment_vote_or_authentication(self):
        self.client.force_login(self.member)
        counts = (Comment.objects.count(), Vote.objects.count())
        urls = (
            reverse("news:comment-create", args=[self.post.pk]),
            reverse("news:post-vote", args=[self.post.pk]),
            reverse("accounts:logout"),
        )
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(counts, (Comment.objects.count(), Vote.objects.count()))
        self.assertIn("_auth_user_id", self.client.session)

    def test_hostile_comment_text_is_escaped_in_public_response(self):
        self.comment.body = '<script>alert("sample")</script>'
        self.comment.save()
        response = self.client.get(reverse("news:post-detail", args=[self.post.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, self.comment.body)
