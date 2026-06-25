from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema
from accounts.models import Profile, UserWallet
from .serializers import ProfileSerializer, UserWalletSerializer


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
# PROFILE (VIEW ONLY)
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=ProfileSerializer,
        tags=["Profile"]
    )
)
class ProfileViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        profile = Profile.objects.filter(user=request.user).first()

        if not profile:
            return self.error(
                message="Profile not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = ProfileSerializer(profile)

        return self.success(
            data=serializer.data,
            message="Profile fetched successfully"
        )


# -------------------------
# DEPOSIT (USER WALLETS ONLY)
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=UserWalletSerializer(many=True),
        tags=["Deposit"]
    )
)
class DepositViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        wallets = UserWallet.objects.filter(user=request.user)

        serializer = UserWalletSerializer(wallets, many=True)

        return self.success(
            data=serializer.data,
            message="User wallets fetched successfully"
        )