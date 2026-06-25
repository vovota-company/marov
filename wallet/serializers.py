from rest_framework import serializers
from .models import Coin, Wallet


class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = [
            "id",
            "network",
            "coin",
            "label",
            "icon",
            "created_at",
        ]


class WalletSerializer(serializers.ModelSerializer):
    coin = CoinSerializer(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "id",
            "balance",
            "coin",
            "created_at",
        ]