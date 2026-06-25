from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Wallet
from .serializers import WalletSerializer

@extend_schema_view(
    list=extend_schema(responses=WalletSerializer(many=True), tags=["Wallet"]),
    retrieve=extend_schema(responses=WalletSerializer, tags=["Wallet"]),
)
class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Wallet.objects
            .filter(user=self.request.user)
            .select_related("coin")
            .order_by("coin__label")
        )