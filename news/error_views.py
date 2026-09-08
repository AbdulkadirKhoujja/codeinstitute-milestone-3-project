"""Plain-language error handlers that never expose exception details."""

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string


def bad_request(request, exception):
    """Render the custom HTTP 400 response."""
    del exception
    return render(request, "400.html", status=400)


def permission_denied(request, exception):
    """Render the custom HTTP 403 response."""
    del exception
    return render(request, "403.html", status=403)


def page_not_found(request, exception):
    """Render the custom HTTP 404 response."""
    del exception
    return render(request, "404.html", status=404)


def server_error(request):
    """Render without session/auth context that may depend on a failed DB."""
    return HttpResponse(render_to_string("500.html"), status=500)


def csrf_failure(request, reason=""):
    """Explain a rejected form without exposing token or diagnostic details."""
    return render(request, "403.html", {"csrf_failure": True}, status=403)
