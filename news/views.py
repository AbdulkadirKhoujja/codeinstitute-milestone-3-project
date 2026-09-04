from django.db.models import Q
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
    """Show a public story or its owner's private draft preview."""
    visible_posts = Post.objects.filter(status=Post.Status.PUBLISHED)
    if request.user.is_authenticated:
        visible_posts = Post.objects.filter(
            Q(status=Post.Status.PUBLISHED) | Q(author=request.user)
        )
    post = get_object_or_404(
        visible_posts.select_related("author", "category"),
        pk=pk,
    )
    return render(request, "news/post-detail.html", {"post": post})
