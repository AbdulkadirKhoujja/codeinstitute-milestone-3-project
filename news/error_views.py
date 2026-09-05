"""Plain-language error handlers that never expose exception details."""

from django.shortcuts import render


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
    """Render the custom HTTP 500 response."""
    return render(request, "500.html", status=500)
