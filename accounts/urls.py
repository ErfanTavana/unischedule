# accounts/urls.py
from django.urls import path
from accounts import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password/", views.change_password_view, name="change-password"),
    path("institution/logo/", views.institution_logo_view, name="institution-logo"),
]
