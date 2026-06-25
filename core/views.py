from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import PlatformWallet, Deposit


class PlatformWalletView(APIView):
    """
    GET /api/core/platform-wallet/
    Admin only. Returns the aggregated user balance per coin (sum of all
    user wallets). Updated in real time by deposit/withdrawal events +
    a 60s periodic Celery beat task as a safety net.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        wallets = PlatformWallet.objects.select_related("coin").all()
        data = [
            {
                "coin":        w.coin.label,
                "network":     w.coin.network,
                "symbol":      w.coin.coin,
                "contract":    w.coin.contract,
                "balance":     str(w.balance),
                "last_synced": w.last_synced_at,
            }
            for w in wallets
        ]
        return Response(data)


class RecentDepositsView(APIView):
    """
    GET /api/core/deposits/
    Admin only. Last 100 deposit events across all users and coins.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        deposits = (
            Deposit.objects
            .select_related("user", "coin")
            .order_by("-created_at")[:100]
        )
        data = [
            {
                "user":    d.user.username,
                "coin":    d.coin.label,
                "amount":  str(d.amount),
                "tx_hash": d.tx_hash,
                "status":  d.status,
                "created": d.created_at,
            }
            for d in deposits
        ]
        return Response(data)