from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .models import Post


def post_list(request):
    """Render ByteBoard's public home page."""
    posts = Post.objects.filter(
        status=Post.Status.PUBLISHED,
    ).select_related("author", "category")
    return render(request, "news/post-list.html", {"posts": posts})


def post_detail(request, pk):
    """Show one published story and its original source."""
    post = get_object_or_404(
        Post.objects.select_related("author", "category"),
        pk=pk,
        status=Post.Status.PUBLISHED,
    )
    return render(request, "news/post-detail.html", {"post": post})
