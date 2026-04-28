from django.urls import path

from apps.posts.views.like import PostLikeView

urlpatterns = [
    path("<int:post_id>/like", PostLikeView.as_view(), name="post-like"),
]
