from django.shortcuts import render

from .forms import RegistrationForm


def register(request):
    """Show the account registration form."""
    form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})
