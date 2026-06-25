from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import PaymentMethod, Currency, SellOffer, BuyOffer
from .serializers import (
    PaymentMethodSerializer,
    CurrencySerializer,
    SellOfferSerializer,
    BuyOfferSerializer
)


class CustomResponseMixin:
    def success(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({
            "success": True,
            "message": message,
            "data": data
        }, status=status_code)

    def error(self, message="Error", status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "success": False,
            "message": message,
            "data": None
        }, status=status_code)


# -------------------------
# PAYMENT METHOD
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=PaymentMethodSerializer(many=True),
        tags=["P2P"]
    ),
    create=extend_schema(
        request=PaymentMethodSerializer,
        responses=PaymentMethodSerializer,
        tags=["P2P"]
    )
)
class PaymentMethodViewSet(CustomResponseMixin, viewsets.ViewSet):

    def list(self, request):
        qs = PaymentMethod.objects.all()
        return self.success(PaymentMethodSerializer(qs, many=True).data)

    def create(self, request):
        serializer = PaymentMethodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(serializer.data, "Created", status.HTTP_201_CREATED)


# -------------------------
# CURRENCY
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=CurrencySerializer(many=True),
        tags=["P2P"]
    ),
    create=extend_schema(
        request=CurrencySerializer,
        responses=CurrencySerializer,
        tags=["P2P"]
    )
)
class CurrencyViewSet(CustomResponseMixin, viewsets.ViewSet):

    def list(self, request):
        qs = Currency.objects.all()
        return self.success(CurrencySerializer(qs, many=True).data)

    def create(self, request):
        serializer = CurrencySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(serializer.data, "Created", status.HTTP_201_CREATED)


# -------------------------
# SELL OFFER
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=SellOfferSerializer(many=True),
        tags=["P2P"]
    ),
    create=extend_schema(
        request=SellOfferSerializer,
        responses=SellOfferSerializer,
        tags=["P2P"]
    )
)
class SellOfferViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = SellOffer.objects.all().order_by("-created_at")
        return self.success(SellOfferSerializer(qs, many=True).data)

    def create(self, request):
        serializer = SellOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return self.success(
            serializer.data,
            "Sell offer created",
            status.HTTP_201_CREATED
        )


# -------------------------
# BUY OFFER
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=BuyOfferSerializer(many=True),
        tags=["P2P"]
    ),
    create=extend_schema(
        request=BuyOfferSerializer,
        responses=BuyOfferSerializer,
        tags=["P2P"]
    )
)
class BuyOfferViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = BuyOffer.objects.all().order_by("-created_at")
        return self.success(BuyOfferSerializer(qs, many=True).data)

    def create(self, request):
        serializer = BuyOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return self.success(
            serializer.data,
            "Buy offer created",
            status.HTTP_201_CREATED
        )