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

    def test_invalid_vote_values_return_bad_request_without_writing(self):
        for value in ("", "0", "2", "not-a-number"):
            with self.subTest(value=value):
                response = self.client.post(
                    reverse("news:post-vote", args=[self.post.pk]),
                    {"value": value},
                )

                self.assertEqual(response.status_code, 400)
                self.assertContains(
                    response,
                    "Choose upvote or downvote.",
                    status_code=400,
                )
                self.assertFalse(Vote.objects.exists())

    def test_anonymous_member_is_sent_to_login_without_writing(self):
        self.client.logout()

        response = self.client.post(
            reverse("news:post-vote", args=[self.post.pk]),
            {"value": Vote.Value.UPVOTE},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
        self.assertFalse(Vote.objects.exists())

    def test_unpublished_and_missing_stories_are_not_votable(self):
        self.post.status = Post.Status.DRAFT
        self.post.save(update_fields=["status"])

        draft_response = self.client.post(
            reverse("news:post-vote", args=[self.post.pk]),
            {"value": Vote.Value.UPVOTE},
        )
        missing_response = self.client.post(
            reverse("news:post-vote", args=[self.post.pk + 999]),
            {"value": Vote.Value.UPVOTE},
        )

        self.assertEqual(draft_response.status_code, 404)
        self.assertEqual(missing_response.status_code, 404)
        self.assertFalse(Vote.objects.exists())

    def test_vote_endpoint_only_accepts_post(self):
        vote_url = reverse("news:post-vote", args=[self.post.pk])

        self.assertEqual(self.client.get(vote_url).status_code, 405)
        self.assertEqual(self.client.put(vote_url).status_code, 405)

    def test_members_have_independent_votes(self):
        other_member = get_user_model().objects.create_user(
            username="other-voter",
            password="Existing-passphrase-284!",
        )
        Vote.objects.create(
            post=self.post,
            user=self.member,
            value=Vote.Value.UPVOTE,
        )
        self.client.force_login(other_member)

        self.client.post(
            reverse("news:post-vote", args=[self.post.pk]),
            {"value": Vote.Value.DOWNVOTE},
        )

        self.assertEqual(Vote.objects.filter(post=self.post).count(), 2)
        self.assertEqual(
            Vote.objects.get(post=self.post, user=self.member).value,
            Vote.Value.UPVOTE,
        )
        self.assertEqual(
            Vote.objects.get(post=self.post, user=other_member).value,
            Vote.Value.DOWNVOTE,
        )
