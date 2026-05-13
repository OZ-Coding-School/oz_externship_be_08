from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include("apps.courses.urls.course_cohorts_url")),
    path("", include("apps.courses.urls.subject_url")),
    path("", include("apps.courses.urls.course_crud")),
]
