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



class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ["password"]



class SellOfferSerializer(serializers.ModelSerializer):
    # READ (nested)
    user = UserDetailSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    coin = CoinSerializer(read_only=True)

    # WRITE (IDs)
    payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.all(),
        source="payment_method",
        write_only=True
    )

    # WRITE
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False
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
            "user", "user_id",
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
    user = UserDetailSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    coin = CoinSerializer(read_only=True)

    payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.all(),
        source="payment_method",
        write_only=True
    )

    # WRITE
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False
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
            "user", "user_id",
            "payment_method", "payment_method_id",
            "currency", "currency_id",
            "coin", "coin_id",
            "exchange_amount",
            "min_money",
            "max_money",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]