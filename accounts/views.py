from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import LoginForm
from .forms import RegistrationForm


class ByteBoardLoginView(LoginView):
    """Authenticate members using Django's established security controls."""

    authentication_form = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Welcome back, {form.get_user().username}.",
        )
        return response


def register(request):
    """Create an account and begin an authenticated session."""
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
