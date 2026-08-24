from django.contrib import admin

from .models import Category, Post


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
