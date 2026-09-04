from django.urls import path

from . import views


app_name = "news"

urlpatterns = [
    path("", views.post_list, name="home"),
    path("posts/<int:pk>/", views.post_detail, name="post-detail"),
]
