from django.urls import path
from locations import views

urlpatterns = [
    path("buildings/", views.list_buildings_view, name="list-buildings"),
    path("buildings/create/", views.create_building_view, name="create-building"),
    path("buildings/<int:building_id>/", views.retrieve_building_view, name="retrieve-building"),
    path("buildings/<int:building_id>/update/", views.update_building_view, name="update-building"),
    path("buildings/<int:building_id>/delete/", views.delete_building_view, name="delete-building"),

    # 🔹 دریافت تمام کلاس‌ها در موسسه (بدون وابستگی به ساختمان خاص)
    path("classrooms/all/", views.list_all_classrooms_view, name="list-all-classrooms"),

    # 🔹 لیست و ساخت کلاس برای یک ساختمان خاص
    path("buildings/<int:building_id>/classrooms/", views.list_classrooms_view, name="list-classrooms"),
    path("buildings/<int:building_id>/classrooms/create/", views.create_classroom_view, name="create-classroom"),

    # 🔹 دریافت / ویرایش / حذف یک کلاس خاص، با بررسی تعلق به institution
    path("classrooms/<int:classroom_id>/", views.retrieve_classroom_view, name="retrieve-classroom"),
    path("classrooms/<int:classroom_id>/update/", views.update_classroom_view, name="update-classroom"),
    path("classrooms/<int:classroom_id>/delete/", views.delete_classroom_view, name="delete-classroom"),
]
