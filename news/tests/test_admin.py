from django.contrib import admin as django_admin
from django.test import TestCase

from news.admin import CategoryAdmin, CommentAdmin, PostAdmin, VoteAdmin
from news.models import Category, Comment, Post, Vote


class AdminRegistrationTests(TestCase):
    """Verify domain models and useful configuration in Django Admin."""

    def test_category_is_registered_with_category_admin(self):
        self.assertIsInstance(
            django_admin.site._registry[Category],
            CategoryAdmin,
        )

    def test_category_slug_is_prepopulated(self):
        model_admin = django_admin.site._registry[Category]

        self.assertEqual(model_admin.prepopulated_fields, {"slug": ("name",)})
        self.assertIn("name", model_admin.search_fields)

    def test_post_is_registered_with_post_admin(self):
        self.assertIsInstance(django_admin.site._registry[Post], PostAdmin)

    def test_post_admin_supports_status_and_category_filtering(self):
        model_admin = django_admin.site._registry[Post]

        self.assertIn("status", model_admin.list_filter)
        self.assertIn("category", model_admin.list_filter)
        self.assertEqual(model_admin.date_hierarchy, "created_at")

    def test_comment_is_registered_with_comment_admin(self):
        self.assertIsInstance(
            django_admin.site._registry[Comment],
            CommentAdmin,
        )

    def test_comment_admin_supports_approval_filtering(self):
        model_admin = django_admin.site._registry[Comment]

        self.assertIn("is_approved", model_admin.list_filter)
        self.assertIn("body", model_admin.search_fields)

    def test_vote_is_registered_with_vote_admin(self):
        self.assertIsInstance(django_admin.site._registry[Vote], VoteAdmin)

    def test_vote_admin_exposes_value_and_user_search(self):
        model_admin = django_admin.site._registry[Vote]

        self.assertIn("value", model_admin.list_display)
        self.assertIn("value", model_admin.list_filter)
        self.assertIn("user__username", model_admin.search_fields)
