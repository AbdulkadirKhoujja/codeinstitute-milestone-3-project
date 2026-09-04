from django.shortcuts import render


def post_list(request):
    """Render ByteBoard's public home page."""
    return render(request, "news/post-list.html")
