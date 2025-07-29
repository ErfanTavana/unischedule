from django.urls import path
from courses.views import course_view

urlpatterns = [
    path("", course_view.list_courses_view, name="list-courses"),
    path("create/", course_view.create_course_view, name="create-course"),
    path("<int:course_id>/", course_view.retrieve_course_view, name="retrieve-course"),
    path("<int:course_id>/update/", course_view.update_course_view, name="update-course"),
    path("<int:course_id>/delete/", course_view.delete_course_view, name="delete-course"),
]
