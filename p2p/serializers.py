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


# -----------------------------
# My Payment Method
# -----------------------------
class MyPaymentMethodSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False
    )

    payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.all(),
        source="payment_method",
        write_only=True
    )

    class Meta:
        model = MyPaymentMethod
        fields = [
            "id",
            "user",
            "user_id",
            "payment_method",
            "payment_method_id",
            "number",
            "name",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]


# -----------------------------
# Sell Offer
# -----------------------------
class SellOfferSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    payment_methods = MyPaymentMethodSerializer(many=True, read_only=True)
    currency = CurrencySerializer(read_only=True)
    coin = CoinSerializer(read_only=True)

    payment_method_ids = serializers.PrimaryKeyRelatedField(
        queryset=MyPaymentMethod.objects.all(),
        many=True,
        source="payment_methods",
        write_only=True
    )

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
            "user",
            "user_id",
            "payment_methods",
            "payment_method_ids",
            "currency",
            "currency_id",
            "coin",
            "coin_id",
            "exchange_amount",
            "min_money",
            "max_money",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]


# -----------------------------
# Buy Offer
# -----------------------------
class BuyOfferSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    payment_methods = MyPaymentMethodSerializer(many=True, read_only=True)
    currency = CurrencySerializer(read_only=True)
    coin = CoinSerializer(read_only=True)

    payment_method_ids = serializers.PrimaryKeyRelatedField(
        queryset=MyPaymentMethod.objects.all(),
        many=True,
        source="payment_methods",
        write_only=True
    )

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
            "user",
            "user_id",
            "payment_methods",
            "payment_method_ids",
            "currency",
            "currency_id",
            "coin",
            "coin_id",
            "exchange_amount",
            "min_money",
            "max_money",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]


# -----------------------------
# Sell Order
# -----------------------------
class SellOrderSerializer(serializers.ModelSerializer):
    sell_offer = SellOfferSerializer(read_only=True)
    seller = UserDetailSerializer(read_only=True)
    client = UserDetailSerializer(read_only=True)
    client_payment_method = MyPaymentMethodSerializer(read_only=True)

    sell_offer_id = serializers.PrimaryKeyRelatedField(
        queryset=SellOffer.objects.all(),
        source="sell_offer",
        write_only=True
    )

    seller_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="seller",
        write_only=True
    )

    client_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="client",
        write_only=True
    )

    client_payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=MyPaymentMethod.objects.all(),
        source="client_payment_method",
        write_only=True
    )

    class Meta:
        model = SellOrder
        fields = [
            "id",
            "sell_offer",
            "sell_offer_id",
            "seller",
            "seller_id",
            "client",
            "client_id",
            "client_payment_method",
            "client_payment_method_id",
            "amount",
            "created_at",
        ]
        read_only_fields = ["created_at"]


# -----------------------------
# Buy Order
# -----------------------------
class BuyOrderSerializer(serializers.ModelSerializer):
    buy_offer = BuyOfferSerializer(read_only=True)
    buyer = UserDetailSerializer(read_only=True)
    client = UserDetailSerializer(read_only=True)
    client_payment_method = MyPaymentMethodSerializer(read_only=True)

    buy_offer_id = serializers.PrimaryKeyRelatedField(
        queryset=BuyOffer.objects.all(),
        source="buy_offer",
        write_only=True
    )

    buyer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="buyer",
        write_only=True
    )

    client_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="client",
        write_only=True
    )

    client_payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=MyPaymentMethod.objects.all(),
        source="client_payment_method",
        write_only=True
    )

    class Meta:
        model = BuyOrder
        fields = [
            "id",
            "buy_offer",
            "buy_offer_id",
            "buyer",
            "buyer_id",
            "client",
            "client_id",
            "client_payment_method",
            "client_payment_method_id",
            "amount",
            "created_at",
        ]
        read_only_fields = ["created_at"]