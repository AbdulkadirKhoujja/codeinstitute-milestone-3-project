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


class VoteActionTests(TestCase):
    def setUp(self):
        self.member = get_user_model().objects.create_user(
            username="active-voter",
            password="Existing-passphrase-284!",
        )
        author = get_user_model().objects.create_user(
            username="active-vote-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Vote actions",
            slug="vote-actions",
            description="Vote action stories.",
        )
        self.post = Post.objects.create(
            title="A story ready for votes",
            summary="Vote action summary.",
            article_url="https://example.com/vote-actions",
            content="Vote action context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        self.client.force_login(self.member)

    def test_initial_upvote_and_downvote_create_allowlisted_values(self):
        for value in (Vote.Value.UPVOTE, Vote.Value.DOWNVOTE):
            with self.subTest(value=value):
                Vote.objects.all().delete()

                response = self.client.post(
                    reverse("news:post-vote", args=[self.post.pk]),
                    {"value": value},
                    follow=True,
                )

                vote = Vote.objects.get(post=self.post, user=self.member)
                self.assertEqual(vote.value, value)
                detail_url = reverse("news:post-detail", args=[self.post.pk])
                self.assertRedirects(
                    response,
                    f"{detail_url}#rating-heading",
                )
                self.assertContains(response, f"Score {value}")
                self.assertContains(response, "Your vote was recorded.")

    def test_opposite_vote_changes_existing_record_in_both_directions(self):
        cases = (
            (Vote.Value.UPVOTE, Vote.Value.DOWNVOTE),
            (Vote.Value.DOWNVOTE, Vote.Value.UPVOTE),
        )
        for initial_value, new_value in cases:
            with self.subTest(initial_value=initial_value, new_value=new_value):
                Vote.objects.all().delete()
                vote = Vote.objects.create(
                    post=self.post,
                    user=self.member,
                    value=initial_value,
                )

                response = self.client.post(
                    reverse("news:post-vote", args=[self.post.pk]),
                    {"value": new_value},
                    follow=True,
                )

                vote.refresh_from_db()
                self.assertEqual(vote.value, new_value)
                self.assertEqual(
                    Vote.objects.filter(
                        post=self.post,
                        user=self.member,
                    ).count(),
                    1,
                )
                self.assertContains(response, "Your vote was changed.")

    def test_repeating_a_vote_removes_it_in_both_directions(self):
        for value in (Vote.Value.UPVOTE, Vote.Value.DOWNVOTE):
            with self.subTest(value=value):
                Vote.objects.all().delete()
                Vote.objects.create(
                    post=self.post,
                    user=self.member,
                    value=value,
                )

                response = self.client.post(
                    reverse("news:post-vote", args=[self.post.pk]),
                    {"value": value},
                    follow=True,
                )

                self.assertFalse(
                    Vote.objects.filter(
                        post=self.post,
                        user=self.member,
                    ).exists()
                )
                self.assertContains(response, "Score 0")
                self.assertContains(response, "Your vote was removed.")
