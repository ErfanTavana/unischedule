from django.urls import path
from semesters.views import (
    list_semesters_view,
    create_semester_view,
    update_semester_view,
    delete_semester_view,
    set_active_semester_view,
)

app_name = "semesters"

urlpatterns = [
    path("", list_semesters_view, name="list-semesters"),
    path("create/", create_semester_view, name="create-semester"),
    path("<int:semester_id>/update/", update_semester_view, name="update-semester"),
    path("<int:semester_id>/delete/", delete_semester_view, name="delete-semester"),
    path("<int:semester_id>/activate/", set_active_semester_view, name="set-active-semester"),
]
