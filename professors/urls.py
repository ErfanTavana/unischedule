from django.urls import path
from professors.views import (
    list_professors_view,
    retrieve_professor_view,
    create_professor_view,
    update_professor_view,
    delete_professor_view,
)

urlpatterns = [
    path("", list_professors_view, name="list-professors"),  # GET /api/professors/
    path("<int:professor_id>/", retrieve_professor_view, name="retrieve-professor"),  # GET /api/professors/<id>/
    path("create/", create_professor_view, name="create-professor"),  # POST /api/professors/create/
    path("<int:professor_id>/update/", update_professor_view, name="update-professor"),  # PUT /api/professors/<id>/update/
    path("<int:professor_id>/delete/", delete_professor_view, name="delete-professor"),  # DELETE /api/professors/<id>/delete/
]
