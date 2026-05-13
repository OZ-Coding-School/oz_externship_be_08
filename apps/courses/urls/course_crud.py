from django.urls import path

from apps.courses.views.course_crud import (
    AdminCourseCreateView,
    AdminCourseDetailView,
    CourseListView,
)
from apps.courses.views.presigned_url_view import CoursePresignedUrlView

urlpatterns = [
    path("course/", CourseListView.as_view(), name="course-list"),
    path("course/presigned-url/", CoursePresignedUrlView.as_view(), name="course-presigned-url"),
    path("admin/courses/", AdminCourseCreateView.as_view(), name="admin-course-create"),
    path("admin/courses/<int:course_id>/", AdminCourseDetailView.as_view(), name="admin-course-detail"),
]
