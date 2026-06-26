from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import *
from .serializers import *


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
# MY PAYMENT METHOD
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=MyPaymentMethodSerializer(many=True),
        tags=["P2P"]
    ),
    create=extend_schema(
        request=MyPaymentMethodSerializer,
        responses=MyPaymentMethodSerializer,
        tags=["P2P"]
    )
)
class MyPaymentMethodViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = MyPaymentMethod.objects.filter(user=request.user).order_by("-created_at")
        return self.success(MyPaymentMethodSerializer(qs, many=True).data)

    def create(self, request):
        serializer = MyPaymentMethodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return self.success(
            serializer.data,
            "Payment method added",
            status.HTTP_201_CREATED
        )


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


# -------------------------
# SELL ORDER
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=SellOrderSerializer(many=True),
        tags=["P2P"]
    ),
    create=extend_schema(
        request=SellOrderSerializer,
        responses=SellOrderSerializer,
        tags=["P2P"]
    )
)
class SellOrderViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = SellOrder.objects.all().order_by("-created_at")
        return self.success(SellOrderSerializer(qs, many=True).data)

    def create(self, request):
        serializer = SellOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success(
            serializer.data,
            "Sell order created",
            status.HTTP_201_CREATED
        )


# -------------------------
# BUY ORDER
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=BuyOrderSerializer(many=True),
        tags=["P2P"]
    ),
    create=extend_schema(
        request=BuyOrderSerializer,
        responses=BuyOrderSerializer,
        tags=["P2P"]
    )
)
class BuyOrderViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = BuyOrder.objects.all().order_by("-created_at")
        return self.success(BuyOrderSerializer(qs, many=True).data)

    def create(self, request):
        serializer = BuyOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success(
            serializer.data,
            "Buy order created",
            status.HTTP_201_CREATED
        )


# -------------------------
# COIN
# -------------------------
@extend_schema_view(
    list=extend_schema(
        responses=CoinSerializer(many=True),
        tags=["Wallet"]
    ),
    create=extend_schema(
        request=CoinSerializer,
        responses=CoinSerializer,
        tags=["Wallet"]
    )
)
class CoinViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = Coin.objects.all().order_by("id")
        return self.success(CoinSerializer(qs, many=True).data)

    def create(self, request):
        serializer = CoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success(
            serializer.data,
            "Coin created",
            status.HTTP_201_CREATED
        )