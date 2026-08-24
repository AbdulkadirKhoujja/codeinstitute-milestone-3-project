from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

from .models import Category, Comment, Post, Vote


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


class PostModelTests(TestCase):
    """Verify post ownership, category protection, status, and ordering."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="post-author",
            password="test-password-123",
        )
        cls.category = Category.objects.create(
            name="Software Development",
            slug="software-development",
            description="Software engineering stories.",
        )
        cls.older_post = Post.objects.create(
            title="Earlier story",
            summary="An earlier summary.",
            article_url="https://example.com/earlier",
            content="Earlier editorial context.",
            author=cls.user,
            category=cls.category,
        )
        cls.newer_post = Post.objects.create(
            title="Later story",
            summary="A later summary.",
            article_url="https://example.com/later",
            content="Later editorial context.",
            author=cls.user,
            category=cls.category,
            status=Post.Status.PUBLISHED,
        )
        now = timezone.now()
        Post.objects.filter(pk=cls.older_post.pk).update(
            created_at=now - timedelta(days=1),
        )
        Post.objects.filter(pk=cls.newer_post.pk).update(created_at=now)

    def test_string_representation_uses_title(self):
        self.assertEqual(str(self.older_post), "Earlier story")

    def test_default_ordering_is_newest_first(self):
        self.assertQuerySetEqual(
            Post.objects.all(),
            [self.newer_post, self.older_post],
        )

    def test_status_choices_and_default(self):
        status_field = Post._meta.get_field("status")

        self.assertEqual(
            list(status_field.choices),
            [("draft", "Draft"), ("published", "Published")],
        )
        self.assertEqual(self.older_post.status, Post.Status.DRAFT)

    def test_author_relationship_is_required(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Post.objects.create(
                title="No author",
                summary="Invalid post.",
                article_url="https://example.com/no-author",
                content="Missing its required author.",
                category=self.category,
            )

    def test_category_relationship_is_required(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Post.objects.create(
                title="No category",
                summary="Invalid post.",
                article_url="https://example.com/no-category",
                content="Missing its required category.",
                author=self.user,
            )

    def test_category_deletion_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()

        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
        self.assertEqual(Post.objects.filter(category=self.category).count(), 2)


class CommentModelTests(TestCase):
    """Verify comment relationships, moderation default, order, and cascade."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="comment-author",
            password="test-password-123",
        )
        cls.category = Category.objects.create(
            name="Cybersecurity",
            slug="cybersecurity",
            description="Security news and research.",
        )
        cls.post = Post.objects.create(
            title="Security story",
            summary="A security summary.",
            article_url="https://example.com/security",
            content="Security context.",
            author=cls.user,
            category=cls.category,
            status=Post.Status.PUBLISHED,
        )
        cls.older_comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            body="First contribution.",
        )
        cls.newer_comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            body="Second contribution.",
            is_approved=True,
        )
        now = timezone.now()
        Comment.objects.filter(pk=cls.older_comment.pk).update(
            created_at=now - timedelta(days=1),
        )
        Comment.objects.filter(pk=cls.newer_comment.pk).update(created_at=now)

    def test_string_representation_identifies_author_and_post(self):
        self.assertEqual(
            str(self.older_comment),
            "Comment by comment-author on Security story",
        )

    def test_default_ordering_is_oldest_first(self):
        self.assertQuerySetEqual(
            Comment.objects.all(),
            [self.older_comment, self.newer_comment],
        )

    def test_comments_are_unapproved_by_default(self):
        self.assertFalse(self.older_comment.is_approved)
        self.assertTrue(self.newer_comment.is_approved)

    def test_post_relationship_is_required(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comment.objects.create(author=self.user, body="Missing post.")

    def test_author_relationship_is_required(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comment.objects.create(post=self.post, body="Missing author.")

    def test_post_deletion_cascades_to_comments(self):
        post_pk = self.post.pk

        self.post.delete()

        self.assertFalse(Post.objects.filter(pk=post_pk).exists())
        self.assertEqual(Comment.objects.count(), 0)


class VoteModelTests(TestCase):
    """Verify vote relationships and database-enforced integrity."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="vote-user",
            password="test-password-123",
        )
        cls.category = Category.objects.create(
            name="Fintech",
            slug="fintech",
            description="Financial technology stories.",
        )
        cls.post = Post.objects.create(
            title="Vote story",
            summary="A story that can be ranked.",
            article_url="https://example.com/vote-story",
            content="Voting context.",
            author=cls.user,
            category=cls.category,
            status=Post.Status.PUBLISHED,
        )
        cls.vote = Vote.objects.create(
            post=cls.post,
            user=cls.user,
            value=Vote.Value.UPVOTE,
        )

    def test_string_representation_identifies_vote(self):
        self.assertEqual(str(self.vote), "vote-user: 1 on Vote story")

    def test_value_choices_are_upvote_and_downvote(self):
        value_field = Vote._meta.get_field("value")

        self.assertEqual(
            list(value_field.choices),
            [(-1, "Downvote"), (1, "Upvote")],
        )

    def test_database_rejects_invalid_vote_value(self):
        other_user = get_user_model().objects.create_user(
            username="invalid-vote-user",
            password="test-password-123",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Vote.objects.create(post=self.post, user=other_user, value=0)

    def test_database_rejects_duplicate_user_post_vote(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vote.objects.create(
                post=self.post,
                user=self.user,
                value=Vote.Value.DOWNVOTE,
            )

    def test_post_relationship_is_required(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vote.objects.create(user=self.user, value=Vote.Value.UPVOTE)

    def test_user_relationship_is_required(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vote.objects.create(post=self.post, value=Vote.Value.UPVOTE)

    def test_post_deletion_cascades_to_votes(self):
        post_pk = self.post.pk

        self.post.delete()

        self.assertFalse(Post.objects.filter(pk=post_pk).exists())
        self.assertEqual(Vote.objects.count(), 0)
