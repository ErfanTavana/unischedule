"""
URL configuration for unischedule project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from displays import urls as display_urls

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/semesters/', include('semesters.urls', namespace='semesters')),

    path("api/professors/", include("professors.urls")),

    path("api/courses/", include("courses.urls")),

    path("api/locations/", include("locations.urls")),

    path("api/auth/", include("accounts.urls")),
    path("api/schedules/", include("schedules.urls")),
    path(
        "api/displays/",
        include((display_urls.api_urlpatterns, "displays"), namespace="displays"),
    ),
    path(
        "displays/",
        include((display_urls.public_urlpatterns, "displays"), namespace="public-displays"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
