from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import PostForm
from .models import Category
from .models import Post


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
    comments = post.comments.filter(is_approved=True).select_related("author")
    return render(
        request,
        "news/post-detail.html",
        {"comments": comments, "post": post},
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
