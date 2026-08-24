from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Category


class CategoryModelTests(TestCase):
    """Verify category display, ordering, and database uniqueness."""

    @classmethod
    def setUpTestData(cls):
        cls.startups = Category.objects.create(
            name="Startups",
            slug="startups",
            description="Startup news and analysis.",
        )
        cls.ai = Category.objects.create(
            name="Artificial Intelligence",
            slug="artificial-intelligence",
            description="Artificial intelligence developments.",
        )

    def test_string_representation_uses_name(self):
        self.assertEqual(str(self.startups), "Startups")

    def test_default_ordering_is_alphabetical(self):
        self.assertQuerySetEqual(
            Category.objects.all(),
            [self.ai, self.startups],
        )

    def test_name_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(
                name=self.startups.name,
                slug="different-slug",
                description="Duplicate name.",
            )

    def test_slug_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(
                name="Different name",
                slug=self.startups.slug,
                description="Duplicate slug.",
            )
