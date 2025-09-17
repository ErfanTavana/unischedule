from django.urls import path

from displays.views import (
    list_display_screens_view,
    create_display_screen_view,
    retrieve_display_screen_view,
    update_display_screen_view,
    delete_display_screen_view,
    list_display_filters_view,
    create_display_filter_view,
    update_display_filter_view,
    delete_display_filter_view,
    public_display_view,
)

app_name = "displays"

api_urlpatterns = [
    path("screens/", list_display_screens_view, name="list-screens"),
    path("screens/create/", create_display_screen_view, name="create-screen"),
    path("screens/<int:screen_id>/", retrieve_display_screen_view, name="retrieve-screen"),
    path("screens/<int:screen_id>/update/", update_display_screen_view, name="update-screen"),
    path("screens/<int:screen_id>/delete/", delete_display_screen_view, name="delete-screen"),
    path("screens/<int:screen_id>/filters/", list_display_filters_view, name="list-filters"),
    path("screens/<int:screen_id>/filters/create/", create_display_filter_view, name="create-filter"),
    path("filters/<int:filter_id>/update/", update_display_filter_view, name="update-filter"),
    path("filters/<int:filter_id>/delete/", delete_display_filter_view, name="delete-filter"),
]

public_urlpatterns = [
    path("<slug:slug>/", public_display_view, name="public-display"),
]

urlpatterns = api_urlpatterns
