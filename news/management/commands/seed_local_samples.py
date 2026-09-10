"""Opt-in fictional records for disposable local verification only."""

import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from news.models import Category, Comment, Post, Vote


TITLES = (
    "A practical checklist for reviewing dependency updates",
    "What a small team can learn from an incident review",
    "Designing useful empty states for a news community",
    "Testing a database migration before a release",
    "Making keyboard focus visible in account forms",
    "Choosing a cache expiry that respects an upstream service",
    "Keeping draft submissions out of public search results",
    "Why an accessible error message needs a clear next step",
    "Reading a query plan before adding another index",
    "Documenting the limits of an automated accessibility check",
    "Using progressive enhancement for community voting",
    "Reviewing external links before publishing a story",
    "Reducing repeated requests during a service outage",
    "Separating a local test database from production records",
    "Moderation decisions that keep technical discussion useful",
    "A longer sample headline about making technology news easier to explore "
    "while keeping source attribution, reader context and a clear distinction "
    "between public stories and private drafts",
)
MARKER = "ByteBoard sample"


class Command(BaseCommand):
    help = "Create labelled samples only in a disposable local database."

    def add_arguments(self, parser):
        parser.add_argument("--confirm-disposable", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirm_disposable"]:
            raise CommandError("Requires --confirm-disposable.")
        database = str(connection.settings_dict["NAME"])
        safe = (
            database in {"byteboard_phase4",
                         "test_byteboard_phase4", ":memory:"}
            or Path(database).name == "byteboard-phase4.sqlite3"
            or database.startswith("file:memorydb_default?")
        )
        if not safe:
            raise CommandError("Refusing a database not reserved for samples.")
        members = []
        for username in ("sample-editor", "sample-reader", "sample-moderator"):
            user, created = get_user_model().objects.get_or_create(
                username=username, defaults={"first_name": MARKER},
            )
            if not created and user.first_name != MARKER:
                raise CommandError("Existing account is not marked as sample.")
            if created:
                # Missing password means unusable; changepassword can set it
                # interactively later. Credentials are never printed.
                user.set_password(os.environ.get("BYTEBOARD_SAMPLE_PASSWORD"))
                user.is_staff = username == "sample-moderator"
                user.save()
            members.append(user)
        members[2].user_permissions.add(*Permission.objects.filter(
            content_type__app_label="news", content_type__model="comment",
            codename__in=("view_comment", "change_comment", "delete_comment"),
        ))
        categories = []
        for label in ("Security", "Platforms", "Design", "Empty"):
            category, _ = Category.objects.get_or_create(
                slug=f"sample-{label.lower()}",
                defaults={"name": f"Sample {label}", "description": MARKER},
            )
            if category.description != MARKER:
                raise CommandError(
                    "Existing category is not marked as sample.")
            categories.append(category)
        posts = []
        for index, title in enumerate(TITLES):
            post, _ = Post.objects.get_or_create(
                author=members[index % 2], title=f"[Sample] {title}",
                defaults={
                    "summary": "Fictional local verification content; "
                               "this is not a report of a real event.",
                    "content": "Discussion exercise: identify one practical "
                               "benefit, one trade-off and a source you would "
                               "check before applying this idea to a project.",
                    "article_url": f"https://example.com/sample-{index + 1}",
                    "category": categories[index % 3],
                    "status": "draft" if index >= 14 else "published",
                },
            )
            posts.append(post)
        for approved, author in ((True, members[0]), (False, members[1])):
            Comment.objects.get_or_create(
                post=posts[0], author=author,
                body=f"[Sample] {'Approved' if approved else 'Pending'} "
                     "discussion: explain the trade-off with a small example.",
                defaults={"is_approved": approved},
            )
        for post, value in ((posts[0], 1), (posts[1], -1)):
            for member in members[:2]:
                Vote.objects.get_or_create(
                    post=post, user=member, defaults={"value": value},
                )
        self.stdout.write("Sample records prepared; no passwords displayed.")
