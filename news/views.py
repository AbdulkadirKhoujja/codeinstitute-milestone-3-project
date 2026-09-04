from django.shortcuts import render

from .models import Post


def post_list(request):
    """Render ByteBoard's public home page."""
    posts = Post.objects.filter(
        status=Post.Status.PUBLISHED,
    ).select_related("author", "category")
    return render(request, "news/post-list.html", {"posts": posts})
