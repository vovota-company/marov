from rest_framework import serializers
from .models import PaymentMethod, Currency, SellOffer, BuyOffer


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = "__all__"
        read_only_fields = ["user", "created_at"]


class BuyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyOffer
        fields = "__all__"
        read_only_fields = ["user", "created_at"]