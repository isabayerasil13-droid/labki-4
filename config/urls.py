from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from bank.views import ClientViewSet, AccountViewSet
router = DefaultRouter()
router.register("clients", ClientViewSet)
router.register("accounts", AccountViewSet)
urlpatterns = [path("", TemplateView.as_view(template_name="index.html")), path("admin/", admin.site.urls), path("api/auth/token/", TokenObtainPairView.as_view()), path("api/auth/refresh/", TokenRefreshView.as_view()), path("api/auth/logout/", TokenBlacklistView.as_view()), path("api/", include(router.urls))]
