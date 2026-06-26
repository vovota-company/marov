from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

# Payment Methods
router.register(r"payment-methods", PaymentMethodViewSet, basename="payment-methods")
router.register(r"my-payment-methods", MyPaymentMethodViewSet, basename="my-payment-methods")

# Currency
router.register(r"currencies", CurrencyViewSet, basename="currencies")

# Offers
router.register(r"sell-offers", SellOfferViewSet, basename="sell-offers")
router.register(r"buy-offers", BuyOfferViewSet, basename="buy-offers")

# Orders
router.register(r"sell-orders", SellOrderViewSet, basename="sell-orders")
router.register(r"buy-orders", BuyOrderViewSet, basename="buy-orders")

# Coins
router.register(r"coins", CoinViewSet, basename="coins")

urlpatterns = [
    path("", include(router.urls)),
]