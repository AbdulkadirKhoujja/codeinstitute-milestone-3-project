from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import RegistrationForm


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
