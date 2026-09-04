from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Post
from news.models import Vote


class VoteScoreDisplayTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="vote-story-author",
            password="Existing-passphrase-284!",
        )
        cls.voters = [
            get_user_model().objects.create_user(
                username=f"score-voter-{index}",
                password="Existing-passphrase-284!",
            )
            for index in range(3)
        ]
        category = Category.objects.create(
            name="Voting",
            slug="voting",
            description="Voting stories.",
        )
        cls.post = Post.objects.create(
            title="A rated community story",
            summary="Rated story summary.",
            article_url="https://example.com/rated-community",
            content="Rated story context.",
            author=cls.author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        Vote.objects.create(
            post=cls.post,
            user=cls.voters[0],
            value=Vote.Value.UPVOTE,
        )
        Vote.objects.create(
            post=cls.post,
            user=cls.voters[1],
            value=Vote.Value.DOWNVOTE,
        )
        Vote.objects.create(
            post=cls.post,
            user=cls.voters[2],
            value=Vote.Value.DOWNVOTE,
        )

    def test_story_detail_displays_aggregate_negative_score(self):
        response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )

        self.assertEqual(response.context["score"], -1)
        self.assertContains(response, 'id="vote-score"')
        self.assertContains(response, "Score -1")
