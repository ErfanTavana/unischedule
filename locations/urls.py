from django.urls import path
from locations.views import building_view

urlpatterns = [
    path("", building_view.list_buildings_view, name="list-buildings"),
    path("create/", building_view.create_building_view, name="create-building"),
    path("<int:building_id>/", building_view.retrieve_building_view, name="retrieve-building"),
    path("<int:building_id>/update/", building_view.update_building_view, name="update-building"),
    path("<int:building_id>/delete/", building_view.delete_building_view, name="delete-building"),
]
