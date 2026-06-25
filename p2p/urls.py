from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import  *

router = DefaultRouter()

router.register(r"payment-methods", PaymentMethodViewSet, basename="payment-methods")
router.register(r"currencies", CurrencyViewSet, basename="currencies")
router.register(r"sell-offers", SellOfferViewSet, basename="sell-offers")
router.register(r"buy-offers", BuyOfferViewSet, basename="buy-offers")
router.register(r"coins", CoinViewSet, basename="coins")

urlpatterns = [
    path("", include(router.urls)),
]