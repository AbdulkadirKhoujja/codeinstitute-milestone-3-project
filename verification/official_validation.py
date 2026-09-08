"""Render isolated samples; upload only with explicit --upload approval."""

import argparse
from io import StringIO
import json
import os
from pathlib import Path
import re
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


def sanitise(html):
    def remove_sensitive_input(match):
        tag = match.group(0)
        if "csrfmiddlewaretoken" in tag:
            return ""
        if 'type="password"' in tag:
            return re.sub(r'\svalue="[^"]*"', "", tag)
        return tag

    cleaned = re.sub(r"<input\b[^>]*>", remove_sensitive_input, html)
    assert "csrfmiddlewaretoken" not in cleaned
    for tag in re.findall(r"<input\b[^>]*>", cleaned):
        assert 'type="password"' not in tag or 'value=' not in tag
    return cleaned


def render_samples():
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "byteboard.settings")
    import django
    from django.conf import settings

    # Override before Django opens any connection: never read private records.
    settings.DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:",
    }}
    settings.ALLOWED_HOSTS = ["testserver"]
    settings.DEBUG = False
    settings.SECURE_SSL_REDIRECT = False
    django.setup()
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
    from django.test import Client, RequestFactory
    from news import error_views
    from news.models import Comment, Post

    call_command("migrate", verbosity=0, stdout=StringIO())
    client = Client()
    pages = {"home-empty": client.get("/")}
    call_command("seed_local_samples", confirm_disposable=True,
                 stdout=StringIO())
    post = Post.objects.get(title__startswith="[Sample] A practical")
    for name, path in {
        "home": "/", "pagination": "/?page=2", "discover": "/discover/",
        "empty-category": "/categories/sample-empty/",
        "detail-public": f"/posts/{post.pk}/", "login": "/accounts/login/",
        "register": "/accounts/register/", "not-found": "/missing-sample/",
    }.items():
        pages[name] = client.get(path)
    pages["login-invalid"] = client.post("/accounts/login/", {})
    pages["register-invalid"] = client.post("/accounts/register/", {
        "username": "sample-validator", "password1": "123", "password2": "123",
    })
    member = get_user_model().objects.get(username="sample-editor")
    client.force_login(member)
    comment = Comment.objects.get(author=member)
    for name, path in {
        "detail-member": f"/posts/{post.pk}/", "post-new": "/posts/new/",
        "post-edit": f"/posts/{post.pk}/edit/",
        "post-delete": f"/posts/{post.pk}/delete/",
        "profile-owner": "/accounts/profile/sample-editor/",
        "comment-edit": f"/posts/{post.pk}/comments/{comment.pk}/edit/",
        "comment-delete": f"/posts/{post.pk}/comments/{comment.pk}/delete/",
    }.items():
        pages[name] = client.get(path)
    pages["post-invalid"] = client.post("/posts/new/", {})
    pages["comment-invalid"] = client.post(
        f"/posts/{post.pk}/comments/{comment.pk}/edit/", {},
    )
    request = RequestFactory().get("/sample-error/")
    pages["bad-request"] = error_views.bad_request(request, Exception())
    pages["permission-denied"] = error_views.permission_denied(request, Exception())
    pages["server-error"] = error_views.server_error(request)
    return {name: sanitise(response.content.decode())
            for name, response in pages.items()}


def submit(url, body, content_type):
    request = Request(url, data=body, headers={
        "Content-Type": content_type, "User-Agent": "ByteBoard validation/1.0",
    })
    try:
        with urlopen(request, timeout=25) as response:
            return response.read().decode()
    except HTTPError as error:
        return json.dumps({"unavailable": f"HTTP {error.code}"})
    except (URLError, TimeoutError):
        return json.dumps({"unavailable": "Connection failure or timeout"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--css", action="store_true")
    parser.add_argument("--page")
    args = parser.parse_args()
    if args.css:
        css = (ROOT / "static/css/style.css").read_text(encoding="utf-8")
        if not args.upload:
            print(f"Custom CSS prepared: {len(css)} characters; no upload.")
            return
        body = urlencode({"text": css, "profile": "css3",
                          "output": "text", "warning": "2"}).encode()
        print(submit("https://jigsaw.w3.org/css-validator/validator", body,
                     "application/x-www-form-urlencoded; charset=utf-8"))
        return
    pages = render_samples()
    if args.page:
        pages = {args.page: pages[args.page]}
    for name, html in pages.items():
        if not args.upload:
            print(f"{name}: {len(html)} characters sanitised; no upload.")
            continue
        result = json.loads(submit("https://validator.w3.org/nu/?out=json",
                                  html.encode(), "text/html; charset=utf-8"))
        messages = result.get("messages", [])
        print(json.dumps({
            "page": name, "version": result.get("version"),
            "errors": sum(item["type"] == "error" for item in messages),
            "warnings": sum(item.get("subType") == "warning" for item in messages),
            "messages": sorted({item["message"] for item in messages}),
            "unavailable": result.get("unavailable"),
        }), flush=True)
        if "unavailable" in result:
            break  # Do not repeatedly burden an unavailable public service.
        sleep(1)


if __name__ == "__main__":
    main()
