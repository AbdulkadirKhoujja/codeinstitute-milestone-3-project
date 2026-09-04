from django.urls import path

from . import views


app_name = "news"

urlpatterns = [
    path("", views.post_list, name="home"),
    path(
        "categories/<slug:category_slug>/",
        views.post_list,
        name="category-feed",
    ),
    path("posts/new/", views.post_create, name="post-create"),
    path("posts/<int:pk>/", views.post_detail, name="post-detail"),
    path("posts/<int:pk>/edit/", views.post_update, name="post-update"),
    path("posts/<int:pk>/delete/", views.post_delete, name="post-delete"),
    path(
        "posts/<int:post_id>/comments/new/",
        views.comment_create,
        name="comment-create",
    ),
    path(
        "posts/<int:post_id>/comments/<int:comment_id>/edit/",
        views.comment_update,
        name="comment-update",
    ),
]
