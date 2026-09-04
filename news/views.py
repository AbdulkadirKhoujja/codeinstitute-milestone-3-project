from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import PostForm
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


@login_required
def post_create(request):
    """Create a story owned by the authenticated member."""
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if post.status == Post.Status.PUBLISHED:
                messages.success(request, "Your story is now published.")
            else:
                messages.success(request, "Your story was saved as a draft.")
            return redirect("news:post-detail", pk=post.pk)
    else:
        form = PostForm()
    return render(
        request,
        "news/post-form.html",
        {"form": form},
    )


@login_required
def post_update(request, pk):
    """Update a story only when requested by its owner."""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            if post.status == Post.Status.PUBLISHED:
                messages.success(request, "Your story changes are now published.")
            else:
                messages.success(request, "Your changes were saved as a draft.")
            return redirect("news:post-detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(
        request,
        "news/post-form.html",
        {
            "form": form,
            "post": post,
        },
    )


@login_required
def post_delete(request, pk):
    """Ask a story owner to confirm a destructive action."""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        post_title = post.title
        post.delete()
        messages.success(request, f"{post_title} was deleted.")
        return redirect("news:home")
    return render(
        request,
        "news/post-confirm-delete.html",
        {"post": post},
    )
