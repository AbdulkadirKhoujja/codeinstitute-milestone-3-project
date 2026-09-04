from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from news.models import Post

from .forms import LoginForm
from .forms import RegistrationForm


class ByteBoardLoginView(LoginView):
    """Authenticate members using Django's established security controls."""

    authentication_form = LoginForm
    redirect_authenticated_user = True
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Welcome back, {form.get_user().username}.",
        )
        return response


class ByteBoardLogoutView(LogoutView):
    """End an authenticated session through a POST request."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "You have been logged out.")
        return response


def profile(request, username):
    """Show public account details and published submissions."""
    profile_user = get_object_or_404(get_user_model(), username=username)
    posts = profile_user.posts.filter(
        status=Post.Status.PUBLISHED,
    ).select_related("category")
    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": profile_user,
            "posts": posts,
        },
    )


def register(request):
    """Create an account and begin an authenticated session."""
    if request.user.is_authenticated:
        return redirect("news:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to ByteBoard, {user.username}.",
            )
            return redirect("news:home")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})
