from django.urls import path
from schedules.views import (
    class_session_view,
    class_cancellation_view,
    makeup_class_view,
)

app_name = "schedules"

urlpatterns = [
    path("", class_session_view.list_class_sessions_view, name="list-class-sessions"),
    path("create/", class_session_view.create_class_session_view, name="create-class-session"),
    path("<int:session_id>/", class_session_view.retrieve_class_session_view, name="retrieve-class-session"),
    path("<int:session_id>/update/", class_session_view.update_class_session_view, name="update-class-session"),
    path("<int:session_id>/delete/", class_session_view.delete_class_session_view, name="delete-class-session"),
    # Class cancellations
    path(
        "cancellations/",
        class_cancellation_view.list_class_cancellations_view,
        name="list-class-cancellations",
    ),
    path(
        "cancellations/create/",
        class_cancellation_view.create_class_cancellation_view,
        name="create-class-cancellation",
    ),
    path(
        "cancellations/<int:cancellation_id>/",
        class_cancellation_view.retrieve_class_cancellation_view,
        name="retrieve-class-cancellation",
    ),
    path(
        "cancellations/<int:cancellation_id>/update/",
        class_cancellation_view.update_class_cancellation_view,
        name="update-class-cancellation",
    ),
    path(
        "cancellations/<int:cancellation_id>/delete/",
        class_cancellation_view.delete_class_cancellation_view,
        name="delete-class-cancellation",
    ),
    # Makeup sessions
    path(
        "makeups/",
        makeup_class_view.list_makeup_class_sessions_view,
        name="list-makeup-class-sessions",
    ),
    path(
        "makeups/create/",
        makeup_class_view.create_makeup_class_session_view,
        name="create-makeup-class-session",
    ),
    path(
        "makeups/<int:makeup_id>/",
        makeup_class_view.retrieve_makeup_class_session_view,
        name="retrieve-makeup-class-session",
    ),
    path(
        "makeups/<int:makeup_id>/update/",
        makeup_class_view.update_makeup_class_session_view,
        name="update-makeup-class-session",
    ),
    path(
        "makeups/<int:makeup_id>/delete/",
        makeup_class_view.delete_makeup_class_session_view,
        name="delete-makeup-class-session",
    ),
]
