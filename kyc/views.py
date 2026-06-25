from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Passport, DrivingLicense, NationalID
from .serializers import (
    PassportSerializer,
    DrivingLicenseSerializer,
    NationalIDSerializer,
    KYCResponseSerializer,
)


class CustomResponseMixin:
    def success(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({
            "success": True,
            "message": message,
            "data": data
        }, status=status_code)

    def error(self, message="Error", status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "success": False,
            "message": message,
            "data": None
        }, status=status_code)


# -------------------------
# PASSPORT
# -------------------------

@extend_schema_view(
    create=extend_schema(
        request=PassportSerializer,
        responses=PassportSerializer,
        tags=["KYC"]
    )
)
class PassportViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = PassportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance, _ = Passport.objects.update_or_create(
            user=request.user,
            defaults=serializer.validated_data
        )

        return self.success(
            data=PassportSerializer(instance).data,
            message="Passport saved successfully",
            status_code=status.HTTP_201_CREATED
        )


# -------------------------
# DRIVING LICENSE
# -------------------------
@extend_schema_view(
    create=extend_schema(
        request=DrivingLicenseSerializer,
        responses=DrivingLicenseSerializer,
        tags=["KYC"]
    )
)
class DrivingLicenseViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = DrivingLicenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance, _ = DrivingLicense.objects.update_or_create(
            user=request.user,
            defaults=serializer.validated_data
        )

        return self.success(
            data=DrivingLicenseSerializer(instance).data,
            message="Driving license saved successfully",
            status_code=status.HTTP_201_CREATED
        )


# -------------------------
# NATIONAL ID
# -------------------------
@extend_schema_view(
    create=extend_schema(
        request=NationalIDSerializer,
        responses=NationalIDSerializer,
        tags=["KYC"]
    )
)
class NationalIDViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = NationalIDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance, _ = NationalID.objects.update_or_create(
            user=request.user,
            defaults=serializer.validated_data
        )

        return self.success(
            data=NationalIDSerializer(instance).data,
            message="National ID saved successfully",
            status_code=status.HTTP_201_CREATED
        )
    
# -------------------------
# KYC VIEW (READ ONLY)
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=KYCResponseSerializer,
        tags=["KYC"]
    )
)
class KYCViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        passport = Passport.objects.filter(user=user).first()
        driving_license = DrivingLicense.objects.filter(user=user).first()
        national_id = NationalID.objects.filter(user=user).first()

        data = {
            "passport": PassportSerializer(passport).data if passport else None,
            "driving_license": DrivingLicenseSerializer(driving_license).data if driving_license else None,
            "national_id": NationalIDSerializer(national_id).data if national_id else None,
            "kyc_status": self._calculate_status(passport, driving_license, national_id)
        }

        return self.success(
            data=data,
            message="KYC fetched successfully"
        )

    def _calculate_status(self, passport, driving_license, national_id):
        """
        Simple KYC logic:
        - If any document exists → pending (you can improve later)
        - If all exist → complete
        - If none → not_started
        """

        if passport and driving_license and national_id:
            return "complete"

        if passport or driving_license or national_id:
            return "pending"

        return "not_started"