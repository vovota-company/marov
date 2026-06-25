from django.db import transaction
import pyotp
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view, extend_schema

from accounts.models import User, UserWallet
from wallet.models import Wallet
from kyc.models import KYC
from accounts.models import Profile
from core.models import DepositAddress

from .models import Withdraw
from .serializers import WithdrawSerializer
from .tasks import process_external_withdrawal


class CustomResponseMixin:
    def success(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({"success": True, "message": message, "data": data}, status=status_code)

    def error(self, message="Error", status_code=status.HTTP_400_BAD_REQUEST):
        return Response({"success": False, "message": message, "data": None}, status=status_code)


@extend_schema_view(
    create=extend_schema(request=WithdrawSerializer, tags=["Withdraw"]),
)
class WithdrawViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coin      = serializer.validated_data["coin"]
        amount    = serializer.validated_data["amount"]
        email     = serializer.validated_data.get("email")
        address   = serializer.validated_data.get("address")
        totp_code = serializer.validated_data["totp_code"]

        # ── KYC ──────────────────────────────────────────────────────────────
        kyc = KYC.objects.filter(user=request.user, status="approved").first()
        if not kyc:
            return self.error(message="KYC must be approved")

        # ── TOTP ─────────────────────────────────────────────────────────────
        profile = Profile.objects.filter(user=request.user).first()
        if not profile:
            return self.error(message="Profile not found")
        if not profile.is_totp_enabled:
            return self.error(message="Authenticator app is not enabled")

        totp = pyotp.TOTP(profile.totp_secret)
        if not totp.verify(totp_code):
            return self.error(message="Invalid authenticator code")

        # ── SENDER WALLET ─────────────────────────────────────────────────────
        sender_wallet = Wallet.objects.select_for_update().filter(
            user=request.user, coin=coin
        ).first()

        if not sender_wallet:
            return self.error(message="Wallet not found")
        if sender_wallet.balance < amount:
            return self.error(message="Insufficient balance")

        # ── DETERMINE: internal or external? ─────────────────────────────────

        receiver_user = None
        is_external   = False

        if email:
            # always internal — find user by email
            receiver_user = User.objects.filter(email=email).first()
            if not receiver_user:
                return self.error(message="User not found")

        elif address:
            # check if address belongs to one of our users (internal)
            internal = DepositAddress.objects.filter(
                address=address,
                coin=coin,
            ).select_related("user").first()

            if internal:
                receiver_user = internal.user
            else:
                # not in our system — external on-chain transfer
                is_external = True
        else:
            return self.error(message="Email or address is required")

        if not is_external and receiver_user == request.user:
            return self.error(message="You cannot transfer to yourself")

        # ── INTERNAL TRANSFER ─────────────────────────────────────────────────
        if not is_external:
            receiver_wallet = Wallet.objects.select_for_update().filter(
                user=receiver_user, coin=coin
            ).first()
            if not receiver_wallet:
                return self.error(message="Receiver wallet not found")

            sender_wallet.balance   -= amount
            sender_wallet.save(update_fields=["balance"])
            receiver_wallet.balance += amount
            receiver_wallet.save(update_fields=["balance"])

            withdraw = Withdraw.objects.create(
                sender=request.user,
                receiver=receiver_user,
                coin=coin,
                amount=amount,
                address=address,
                status=Withdraw.STATUS_INTERNAL,
            )

            return self.success(
                data={"withdraw_id": withdraw.id, "reference": withdraw.reference},
                message="Transfer completed successfully",
                status_code=status.HTTP_201_CREATED,
            )

        # ── EXTERNAL TRANSFER ─────────────────────────────────────────────────
        # 1. reserve balance immediately (deduct now, release if broadcast fails)
        sender_wallet.balance -= amount
        sender_wallet.save(update_fields=["balance"])

        # 2. create a PENDING withdrawal record
        withdraw = Withdraw.objects.create(
            sender=request.user,
            receiver=None,
            coin=coin,
            amount=amount,
            address=address,
            status=Withdraw.STATUS_PENDING,
        )

        # 3. queue the broadcast task OUTSIDE the atomic block
        #    (transaction.on_commit ensures the DB row exists before the task runs)
        transaction.on_commit(
            lambda: process_external_withdrawal.delay(withdraw.id)
        )

        return self.success(
            data={
                "withdraw_id": withdraw.id,
                "reference":   withdraw.reference,
                "status":      withdraw.status,
                "message":     "Your withdrawal is being processed on-chain.",
            },
            message="Withdrawal submitted",
            status_code=status.HTTP_201_CREATED,
        )

    @extend_schema(tags=["Withdraw"])
    @action(detail=False, methods=["get"], url_path="status")
    def withdrawal_status(self, request):
        """
        GET /api/withdraw/status/?reference=<reference>
        Let the frontend poll for the result of an external withdrawal.
        """
        reference = request.query_params.get("reference")
        if not reference:
            return self.error(message="reference is required")

        withdraw = Withdraw.objects.filter(
            reference=reference,
            sender=request.user,
        ).first()

        if not withdraw:
            return self.error(message="Withdrawal not found", status_code=status.HTTP_404_NOT_FOUND)

        return self.success(data={
            "withdraw_id":     withdraw.id,
            "status":          withdraw.status,
            "tx_hash":         withdraw.tx_hash,
            "amount":          str(withdraw.amount),
            "coin":            withdraw.coin.label,
            "address":         withdraw.address,
            "failure_reason":  withdraw.failure_reason,
            "created_at":      withdraw.created_at,
        })