from rest_framework import serializers
from .models import Withdraw


class WithdrawSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=False,
        write_only=True
    )

    totp_code = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = Withdraw
        fields = [
            "id",
            "coin",
            "amount",
            "address",
            "email",
            "totp_code",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]