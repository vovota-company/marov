from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet, DepositViewSet

router = DefaultRouter()

router.register(r"profile", ProfileViewSet, basename="profile")
router.register(r"deposit", DepositViewSet, basename="deposit")

urlpatterns = [
    path("", include(router.urls)),
]