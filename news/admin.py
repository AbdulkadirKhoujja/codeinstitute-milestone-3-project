from django.contrib import admin

from .models import Category, Comment, Post, Vote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "summary", "content", "author__username")
    list_filter = ("status", "category", "created_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("author", "category")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "post",
        "author",
        "is_approved",
        "created_at",
        "updated_at",
    )
    search_fields = ("body", "post__title", "author__username")
    list_filter = ("is_approved", "created_at")
    date_hierarchy = "created_at"
    ordering = ("created_at",)
    list_select_related = ("post", "author")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "value", "created_at")
    search_fields = ("post__title", "user__username")
    list_filter = ("value", "created_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("post", "user")
