from django.conf import settings
from django.conf.urls.static import static
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("api/v1/posts/", include("apps.posts.urls")),
    path("api/v1/", include("apps.qna.urls.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    if "drf_spectacular" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
            path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
            path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
        ]
