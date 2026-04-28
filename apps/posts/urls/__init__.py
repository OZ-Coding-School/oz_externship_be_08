from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include("apps.posts.urls.post_crud")),
    path("", include("apps.posts.urls.like")),
]
