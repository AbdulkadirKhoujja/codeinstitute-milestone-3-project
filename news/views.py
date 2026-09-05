from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .forms import PostForm
from .models import Category
from .models import Comment
from .models import Post
from .models import Vote


SORT_ORDERS = {
    "newest": ("-created_at", "-pk"),
    "highest": ("-score", "-created_at", "-pk"),
    "oldest": ("created_at", "pk"),
    "title": ("title", "pk"),
}
SORT_OPTIONS = (
    ("newest", "Newest first"),
    ("highest", "Highest rated"),
    ("oldest", "Oldest first"),
    ("title", "Title A–Z"),
)


def is_async_request(request):
    """Return whether the caller expects a same-origin JSON response."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def post_detail_context(request, post, comment_form=None):
    """Build the discussion context shared by detail and invalid forms."""
    visible_comments = Q(is_approved=True)
    current_vote = None
    if request.user.is_authenticated:
        visible_comments |= Q(author=request.user)
        comment_form = comment_form or CommentForm()
        if post.status == Post.Status.PUBLISHED:
            current_vote = post.votes.filter(user=request.user).values_list(
                "value",
                flat=True,
            ).first()
    return {
        "comment_form": comment_form,
        "comments": post.comments.filter(visible_comments).select_related(
            "author"
        ),
        "current_vote": current_vote,
        "post": post,
        "score": post.votes.aggregate(
            score=Coalesce(
                Sum("value"),
                Value(0),
                output_field=IntegerField(),
            )
        )["score"],
    }


def post_list(request, category_slug=None):
    """Render ByteBoard's public home page."""
    posts = Post.objects.filter(
        status=Post.Status.PUBLISHED,
    ).select_related("author", "category")
    active_category = None
    category_slug = category_slug or request.GET.get("category")
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=active_category)
    search_query = request.GET.get("q", "").strip()
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(summary__icontains=search_query)
            | Q(content__icontains=search_query)
        )
    active_sort = request.GET.get("sort", "newest")
    if active_sort not in SORT_ORDERS:
        active_sort = "newest"
    if active_sort == "highest":
        posts = posts.annotate(
            score=Coalesce(
                Sum("votes__value"),
                Value(0),
                output_field=IntegerField(),
            )
        )
    posts = posts.order_by(*SORT_ORDERS[active_sort])
    page_obj = Paginator(posts, 10).get_page(request.GET.get("page"))
    pagination_parameters = request.GET.copy()
    pagination_parameters.pop("page", None)
    return render(
        request,
        "news/post-list.html",
        {
            "active_category": active_category,
            "active_sort": active_sort,
            "categories": Category.objects.all(),
            "page_obj": page_obj,
            "pagination_query": pagination_parameters.urlencode(),
            "posts": page_obj.object_list,
            "search_query": search_query,
            "sort_options": SORT_OPTIONS,
        },
    )


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
    return render(
        request,
        "news/post-detail.html",
        post_detail_context(request, post),
    )


@login_required
@require_http_methods(["GET", "POST"])
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
@require_http_methods(["GET", "POST"])
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
@require_http_methods(["GET", "POST"])
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


@login_required
@require_POST
def comment_create(request, post_id):
    """Attach a pending comment to a story visible to the member."""
    visible_posts = Post.objects.filter(
        Q(status=Post.Status.PUBLISHED) | Q(author=request.user)
    )
    post = get_object_or_404(visible_posts, pk=post_id)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "news/post-detail.html",
            post_detail_context(request, post, comment_form=form),
        )
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    messages.success(request, "Your comment is awaiting moderation.")
    return redirect(
        f"{reverse('news:post-detail', args=[post.pk])}#comment-{comment.pk}"
    )


@login_required
@require_http_methods(["GET", "POST"])
def comment_update(request, post_id, comment_id):
    """Update comment content only for its owner."""
    comment = get_object_or_404(
        Comment.objects.select_related("post"),
        pk=comment_id,
        post_id=post_id,
        author=request.user,
    )
    form = CommentForm(request.POST or None, instance=comment)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.is_approved = False
        comment.save()
        messages.success(
            request,
            "Your updated comment is awaiting moderation.",
        )
        return redirect(
            f"{reverse('news:post-detail', args=[post_id])}"
            f"#comment-{comment.pk}"
        )
    return render(
        request,
        "news/comment-form.html",
        {"comment": comment, "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def comment_delete(request, post_id, comment_id):
    """Ask the comment owner to confirm deletion."""
    comment = get_object_or_404(
        Comment.objects.select_related("post"),
        pk=comment_id,
        post_id=post_id,
        author=request.user,
    )
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Your comment was deleted.")
        return redirect(
            f"{reverse('news:post-detail', args=[post_id])}#comments-heading"
        )
    return render(
        request,
        "news/comment-confirm-delete.html",
        {"comment": comment},
    )


@require_POST
def post_vote(request, post_id):
    """Record or change a member's vote on a published story."""
    if not request.user.is_authenticated:
        if is_async_request(request):
            return JsonResponse(
                {"success": False, "message": "Log in to vote."},
                status=401,
            )
        return redirect_to_login(
            request.get_full_path(),
            reverse("accounts:login"),
        )
    post = Post.objects.filter(
        pk=post_id,
        status=Post.Status.PUBLISHED,
    ).first()
    if post is None:
        if is_async_request(request):
            return JsonResponse(
                {"success": False, "message": "Story not found."},
                status=404,
            )
        return get_object_or_404(
            Post,
            pk=post_id,
            status=Post.Status.PUBLISHED,
        )
    raw_value = request.POST.get("value")
    if raw_value not in {str(Vote.Value.UPVOTE), str(Vote.Value.DOWNVOTE)}:
        if is_async_request(request):
            return JsonResponse(
                {
                    "success": False,
                    "message": "Choose upvote or downvote.",
                },
                status=400,
            )
        return HttpResponseBadRequest("Choose upvote or downvote.")
    value = int(raw_value)
    vote = Vote.objects.filter(post=post, user=request.user).first()
    if vote is None:
        Vote.objects.create(post=post, user=request.user, value=value)
        feedback = "Your vote was recorded."
    elif vote.value != value:
        vote.value = value
        vote.save(update_fields=["value"])
        feedback = "Your vote was changed."
    else:
        vote.delete()
        feedback = "Your vote was removed."
    if is_async_request(request):
        score = post.votes.aggregate(
            score=Coalesce(
                Sum("value"),
                Value(0),
                output_field=IntegerField(),
            )
        )["score"]
        current_vote = post.votes.filter(user=request.user).values_list(
            "value",
            flat=True,
        ).first()
        return JsonResponse(
            {
                "success": True,
                "score": score,
                "current_vote": current_vote,
                "message": feedback,
            }
        )
    messages.success(request, feedback)
    return redirect(
        f"{reverse('news:post-detail', args=[post.pk])}#rating-heading"
    )
