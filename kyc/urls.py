from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PassportViewSet,
    DrivingLicenseViewSet,
    NationalIDViewSet,
    KYCViewSet,
)

router = DefaultRouter()

router.register(r"passport", PassportViewSet, basename="passport")
router.register(r"driving-license", DrivingLicenseViewSet, basename="driving-license")
router.register(r"national-id", NationalIDViewSet, basename="national-id")
router.register(r"kyc", KYCViewSet, basename="kyc")

urlpatterns = [
    path("", include(router.urls)),
]