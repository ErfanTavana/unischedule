from django.urls import path
from schedules.views import class_session_view

app_name = "schedules"

urlpatterns = [
    path("", class_session_view.list_class_sessions_view, name="list-class-sessions"),
    path("create/", class_session_view.create_class_session_view, name="create-class-session"),
    path("<int:session_id>/", class_session_view.retrieve_class_session_view, name="retrieve-class-session"),
    path("<int:session_id>/update/", class_session_view.update_class_session_view, name="update-class-session"),
    path("<int:session_id>/delete/", class_session_view.delete_class_session_view, name="delete-class-session"),
]
