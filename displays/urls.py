from django.urls import path

from displays.views import (
    list_display_screens_view,
    create_display_screen_view,
    retrieve_display_screen_view,
    update_display_screen_view,
    delete_display_screen_view,
    public_display_view,
)

app_name = "displays"

api_urlpatterns = [
    path("screens/", list_display_screens_view, name="list-screens"),
    path("screens/create/", create_display_screen_view, name="create-screen"),
    path("screens/<int:screen_id>/", retrieve_display_screen_view, name="retrieve-screen"),
    path("screens/<int:screen_id>/update/", update_display_screen_view, name="update-screen"),
    path("screens/<int:screen_id>/delete/", delete_display_screen_view, name="delete-screen"),
]

# Public preview endpoints are intentionally unauthenticated; they are consumed
# by kiosk/TV clients that only know the screen slug.  Access should be limited
# to opaque slugs shared with trusted devices.
public_urlpatterns = [
    path("<slug:slug>/", public_display_view, name="public-display"),
]

urlpatterns = api_urlpatterns
