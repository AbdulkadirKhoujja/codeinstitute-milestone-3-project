from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Category
from news.models import Post
from news.models import Vote


class PublishedPostFeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="feed-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Startups",
            slug="startups",
            description="Startup stories.",
        )
        cls.older_post = Post.objects.create(
            title="Older published story",
            summary="An older story summary.",
            article_url="https://example.com/older",
            content="Older story context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.newer_post = Post.objects.create(
            title="Newer published story",
            summary="A newer story summary.",
            article_url="https://example.com/newer",
            content="Newer story context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.draft_post = Post.objects.create(
            title="Private draft story",
            summary="A private draft summary.",
            article_url="https://example.com/draft",
            content="Draft context.",
            author=author,
            category=category,
            status=Post.Status.DRAFT,
        )
        now = timezone.now()
        Post.objects.filter(pk=cls.older_post.pk).update(
            created_at=now - timedelta(days=1)
        )
        Post.objects.filter(pk=cls.newer_post.pk).update(created_at=now)

    def test_feed_contains_only_published_posts_newest_first(self):
        response = self.client.get(reverse("news:home"))

        self.assertQuerySetEqual(
            response.context["posts"],
            [self.newer_post, self.older_post],
        )

    def test_feed_renders_accessible_story_cards_with_metadata(self):
        response = self.client.get(reverse("news:home"))

        self.assertTemplateUsed(response, "includes/post-card.html")
        self.assertContains(response, self.newer_post.title)
        self.assertContains(response, self.newer_post.summary)
        self.assertContains(response, self.newer_post.category.name)
        self.assertContains(response, self.newer_post.author.username)
        self.assertContains(
            response,
            f'href="{reverse("news:post-detail", args=[self.newer_post.pk])}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("accounts:profile", args=[self.newer_post.author.username])}"',
        )
        self.assertContains(response, '<time datetime="')
        content = response.content.decode()
        self.assertLess(
            content.index(self.newer_post.title),
            content.index(self.older_post.title),
        )


class CategoryFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="category-author",
            password="Existing-passphrase-284!",
        )
        cls.ai_category = Category.objects.create(
            name="Artificial Intelligence",
            slug="artificial-intelligence",
            description="Artificial intelligence stories.",
        )
        cls.startup_category = Category.objects.create(
            name="Startups",
            slug="startups",
            description="Startup stories.",
        )
        cls.ai_post = Post.objects.create(
            title="AI category story",
            summary="An AI story summary.",
            article_url="https://example.com/ai-category",
            content="AI category context.",
            author=author,
            category=cls.ai_category,
            status=Post.Status.PUBLISHED,
        )
        cls.startup_post = Post.objects.create(
            title="Startup category story",
            summary="A startup story summary.",
            article_url="https://example.com/startup-category",
            content="Startup category context.",
            author=author,
            category=cls.startup_category,
            status=Post.Status.PUBLISHED,
        )

    def test_category_query_narrows_feed_and_identifies_active_filter(self):
        response = self.client.get(
            reverse("news:home"),
            {"category": self.startup_category.slug},
        )

        self.assertQuerySetEqual(response.context["posts"], [self.startup_post])
        self.assertEqual(response.context["active_category"], self.startup_category)
        self.assertContains(response, "Startups stories")
        self.assertContains(response, self.startup_post.title)
        self.assertNotContains(response, self.ai_post.title)
        self.assertContains(response, f'href="{reverse("news:home")}"')

    def test_feed_exposes_categories_in_alphabetical_order(self):
        response = self.client.get(reverse("news:home"))

        self.assertQuerySetEqual(
            response.context["categories"],
            [self.ai_category, self.startup_category],
        )


class StorySearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="search-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Research",
            slug="research",
            description="Technology research stories.",
        )
        cls.title_match = Post.objects.create(
            title="Quantum networking milestone",
            summary="A scientific update.",
            article_url="https://example.com/quantum",
            content="Research context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.summary_match = Post.objects.create(
            title="A new processor",
            summary="Modular hardware reaches production.",
            article_url="https://example.com/hardware",
            content="Processor context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.content_match = Post.objects.create(
            title="Open standards update",
            summary="A standards body reports progress.",
            article_url="https://example.com/standards",
            content="The ContextNeedle appears in this analysis.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.private_match = Post.objects.create(
            title="Quantum draft",
            summary="A private quantum draft.",
            article_url="https://example.com/quantum-draft",
            content="Private context.",
            author=author,
            category=category,
            status=Post.Status.DRAFT,
        )

    def test_search_matches_documented_story_fields_case_insensitively(self):
        cases = (
            ("quantum", self.title_match),
            ("HARDWARE", self.summary_match),
            ("contextneedle", self.content_match),
        )
        for query, expected_post in cases:
            with self.subTest(query=query):
                response = self.client.get(reverse("news:home"), {"q": query})

                self.assertQuerySetEqual(response.context["posts"], [expected_post])
                self.assertNotContains(response, self.private_match.title)

    def test_search_form_and_heading_identify_active_query(self):
        response = self.client.get(reverse("news:home"), {"q": " quantum "})

        self.assertEqual(response.context["search_query"], "quantum")
        self.assertContains(response, '<label for="story-search"')
        self.assertContains(response, 'value="quantum"')
        self.assertContains(response, 'Search results for "quantum"')


class StorySortingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="sorting-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Platforms",
            slug="platforms",
            description="Technology platform stories.",
        )
        cls.alpha_post = Post.objects.create(
            title="Alpha platform story",
            summary="Alpha summary.",
            article_url="https://example.com/alpha",
            content="Alpha context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.zulu_post = Post.objects.create(
            title="Zulu platform story",
            summary="Zulu summary.",
            article_url="https://example.com/zulu",
            content="Zulu context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        now = timezone.now()
        Post.objects.filter(pk=cls.alpha_post.pk).update(
            created_at=now - timedelta(days=1)
        )
        Post.objects.filter(pk=cls.zulu_post.pk).update(created_at=now)

    def test_sort_options_apply_expected_order(self):
        cases = (
            ("newest", [self.zulu_post, self.alpha_post]),
            ("oldest", [self.alpha_post, self.zulu_post]),
            ("title", [self.alpha_post, self.zulu_post]),
            ("untrusted-field", [self.zulu_post, self.alpha_post]),
        )
        for sort_value, expected_posts in cases:
            with self.subTest(sort_value=sort_value):
                response = self.client.get(
                    reverse("news:home"),
                    {"sort": sort_value},
                )

                self.assertQuerySetEqual(response.context["posts"], expected_posts)

    def test_sort_control_identifies_active_safe_option(self):
        response = self.client.get(reverse("news:home"), {"sort": "oldest"})

        self.assertEqual(response.context["active_sort"], "oldest")
        self.assertContains(response, '<label for="story-sort"')
        self.assertContains(response, '<option value="oldest" selected>')


class HighestRatedSortingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="rating-author",
            password="Existing-passphrase-284!",
        )
        cls.voters = [
            get_user_model().objects.create_user(
                username=f"rating-voter-{index}",
                password="Existing-passphrase-284!",
            )
            for index in range(3)
        ]
        category = Category.objects.create(
            name="Ratings",
            slug="ratings",
            description="Rated technology stories.",
        )
        cls.high_post = cls.create_post("High-rated story", category)
        cls.negative_post = cls.create_post("Negative-rated story", category)
        cls.unrated_post = cls.create_post("Unrated story", category)
        Vote.objects.create(
            post=cls.high_post,
            user=cls.voters[0],
            value=Vote.Value.UPVOTE,
        )
        Vote.objects.create(
            post=cls.high_post,
            user=cls.voters[1],
            value=Vote.Value.UPVOTE,
        )
        Vote.objects.create(
            post=cls.negative_post,
            user=cls.voters[0],
            value=Vote.Value.UPVOTE,
        )
        Vote.objects.create(
            post=cls.negative_post,
            user=cls.voters[1],
            value=Vote.Value.DOWNVOTE,
        )
        Vote.objects.create(
            post=cls.negative_post,
            user=cls.voters[2],
            value=Vote.Value.DOWNVOTE,
        )

    @classmethod
    def create_post(cls, title, category):
        return Post.objects.create(
            title=title,
            summary=f"Summary for {title}.",
            article_url="https://example.com/rated-story",
            content="Rated story context.",
            author=cls.author,
            category=category,
            status=Post.Status.PUBLISHED,
        )

    def test_highest_rated_aggregates_positive_negative_and_empty_scores(self):
        response = self.client.get(reverse("news:home"), {"sort": "highest"})

        self.assertQuerySetEqual(
            response.context["posts"],
            [self.high_post, self.unrated_post, self.negative_post],
        )
        self.assertEqual(
            [post.score for post in response.context["posts"]],
            [2, 0, -1],
        )
        self.assertContains(response, '<option value="highest" selected>')
        self.assertContains(response, "Score 2")


class StoryPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="pagination-author",
            password="Existing-passphrase-284!",
        )
        cls.category = Category.objects.create(
            name="Cloud",
            slug="cloud",
            description="Cloud technology stories.",
        )
        for index in range(12):
            Post.objects.create(
                title=f"Page story {index + 1:02d}",
                summary="A pagination test summary.",
                article_url=f"https://example.com/page-{index + 1}",
                content="Pagination test context.",
                author=author,
                category=cls.category,
                status=Post.Status.PUBLISHED,
            )

    def test_feed_paginates_ten_stories_per_page(self):
        first_page = self.client.get(reverse("news:home"))
        second_page = self.client.get(reverse("news:home"), {"page": 2})

        self.assertEqual(len(first_page.context["posts"]), 10)
        self.assertEqual(len(second_page.context["posts"]), 2)
        self.assertEqual(first_page.context["page_obj"].paginator.num_pages, 2)
        self.assertContains(first_page, 'aria-label="Story pages"')
        self.assertContains(first_page, 'href="?page=2"')

    def test_page_links_preserve_active_feed_controls(self):
        response = self.client.get(
            reverse("news:home"),
            {
                "q": "Page",
                "category": self.category.slug,
                "sort": "oldest",
            },
        )

        self.assertContains(
            response,
            "?q=Page&amp;category=cloud&amp;sort=oldest&amp;page=2",
        )


class FeedEmptyStateTests(TestCase):
    def test_feed_explains_when_no_stories_are_published(self):
        response = self.client.get(reverse("news:home"))

        self.assertContains(response, "No published stories yet")
        self.assertContains(response, "Check back soon")

    def test_empty_search_explains_result_and_offers_clear_action(self):
        response = self.client.get(reverse("news:home"), {"q": "missing"})

        self.assertContains(response, 'No stories matched "missing"')
        self.assertContains(response, "Clear filters")
        self.assertContains(response, f'href="{reverse("news:home")}"')


class CombinedFeedControlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="combined-control-author",
            password="Existing-passphrase-284!",
        )
        cls.first_category = Category.objects.create(
            name="Data",
            slug="data",
            description="Data technology stories.",
        )
        cls.second_category = Category.objects.create(
            name="Networks",
            slug="networks",
            description="Networking stories.",
        )
        cls.matching_post = Post.objects.create(
            title="Shared systems insight",
            summary="Combined control summary.",
            article_url="https://example.com/combined-control",
            content="Combined control context.",
            author=author,
            category=cls.first_category,
            status=Post.Status.PUBLISHED,
        )

    def test_controls_preserve_other_active_filters(self):
        response = self.client.get(
            reverse("news:home"),
            {
                "q": "shared systems",
                "category": self.first_category.slug,
                "sort": "oldest",
            },
        )

        self.assertQuerySetEqual(response.context["posts"], [self.matching_post])
        self.assertContains(
            response,
            "/?category=networks&amp;q=shared%20systems&amp;sort=oldest",
        )
        self.assertContains(
            response,
            "/?q=shared%20systems&amp;sort=oldest",
        )
        self.assertContains(response, 'name="sort" type="hidden" value="oldest"')
