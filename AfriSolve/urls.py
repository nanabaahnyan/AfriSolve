"""
URL configuration for AfriSolve project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import (
    home_view, login_view, register_view, logout_view,
    dashboard_view, profile_view, settings_view,
    faq_view, terms_view, privacy_view
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Template Frontend Routes
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/", profile_view, name="profile"),
    path("settings/", settings_view, name="settings"),
    path("faq/", faq_view, name="faq"),
    path("terms/", terms_view, name="terms"),
    path("privacy/", privacy_view, name="privacy"),
    
    # Sub-app Template Routes
    path("problems/", include("problems.template_urls")),
    path("teams/", include("teams.template_urls")),
    path("users/", include("users.template_urls")),
    path("notifications/", include("notifications.template_urls")),

    # REST API Routes (Used by AJAX components)
    path("api/users/", include("users.urls")),
    path("api/problems/", include("problems.urls")),
    path("api/teams/", include("teams.urls")),
    path("api/notifications/", include("notifications.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

