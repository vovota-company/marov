from rest_framework import serializers
from .models import *

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = "__all__"



class SellOfferSerializer(serializers.ModelSerializer):
    # READ (nested)
    payment_method = PaymentMethodSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    coin = CoinSerializer(read_only=True)

    # WRITE (IDs)
    payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.all(),
        source="payment_method",
        write_only=True
    )

    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        source="currency",
        write_only=True
    )

    coin_id = serializers.PrimaryKeyRelatedField(
        queryset=Coin.objects.all(),
        source="coin",
        write_only=True
    )

    class Meta:
        model = SellOffer
        fields = [
            "id",
            "user",
            "payment_method", "payment_method_id",
            "currency", "currency_id",
            "coin", "coin_id",
            "number",
            "name",
            "exchange_amount",
            "min_money",
            "max_money",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]


class BuyOfferSerializer(serializers.ModelSerializer):
    payment_method = PaymentMethodSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    coin = CoinSerializer(read_only=True)

    payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.all(),
        source="payment_method",
        write_only=True
    )

    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        source="currency",
        write_only=True
    )

    coin_id = serializers.PrimaryKeyRelatedField(
        queryset=Coin.objects.all(),
        source="coin",
        write_only=True
    )

    class Meta:
        model = BuyOffer
        fields = [
            "id",
            "user",
            "payment_method", "payment_method_id",
            "currency", "currency_id",
            "coin", "coin_id",
            "exchange_amount",
            "min_money",
            "max_money",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]