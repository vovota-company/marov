from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import *
from .serializers import *


class CustomResponseMixin:
    def success(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
            },
            status=status_code,
        )

    def error(self, message="Error", status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                "success": False,
                "message": message,
                "data": None,
            },
            status=status_code,
        )


# -------------------------
# PAYMENT METHOD
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["P2P"]),
    create=extend_schema(tags=["P2P"]),
)
class PaymentMethodViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(serializer.data, "Created", status.HTTP_201_CREATED)


# -------------------------
# MY PAYMENT METHOD
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["P2P"]),
    create=extend_schema(tags=["P2P"]),
)
class MyPaymentMethodViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    serializer_class = MyPaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    queryset = MyPaymentMethod.objects.all()

    def get_queryset(self):
        return MyPaymentMethod.objects.filter(user=self.request.user).order_by("-created_at")

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return self.success(
            serializer.data,
            "Payment method added",
            status.HTTP_201_CREATED,
        )


# -------------------------
# CURRENCY
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["P2P"]),
    create=extend_schema(tags=["P2P"]),
)
class CurrencyViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(serializer.data, "Created", status.HTTP_201_CREATED)


# -------------------------
# SELL OFFER
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["P2P"]),
    create=extend_schema(tags=["P2P"]),
)
class SellOfferViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    queryset = SellOffer.objects.all().order_by("-created_at")
    serializer_class = SellOfferSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return self.success(
            serializer.data,
            "Sell offer created",
            status.HTTP_201_CREATED,
        )


# -------------------------
# BUY OFFER
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["P2P"]),
    create=extend_schema(tags=["P2P"]),
)
class BuyOfferViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    queryset = BuyOffer.objects.all().order_by("-created_at")
    serializer_class = BuyOfferSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return self.success(
            serializer.data,
            "Buy offer created",
            status.HTTP_201_CREATED,
        )


# -------------------------
# SELL ORDER
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["P2P"]),
    create=extend_schema(tags=["P2P"]),
)
class SellOrderViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    queryset = SellOrder.objects.all().order_by("-created_at")
    serializer_class = SellOrderSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(
            serializer.data,
            "Sell order created",
            status.HTTP_201_CREATED,
        )


# -------------------------
# BUY ORDER
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["P2P"]),
    create=extend_schema(tags=["P2P"]),
)
class BuyOrderViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    queryset = BuyOrder.objects.all().order_by("-created_at")
    serializer_class = BuyOrderSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(
            serializer.data,
            "Buy order created",
            status.HTTP_201_CREATED,
        )


# -------------------------
# COIN
# -------------------------
@extend_schema_view(
    list=extend_schema(tags=["Wallet"]),
    create=extend_schema(tags=["Wallet"]),
)
class CoinViewSet(CustomResponseMixin, viewsets.GenericViewSet):
    queryset = Coin.objects.all().order_by("id")
    serializer_class = CoinSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return self.success(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(
            serializer.data,
            "Coin created",
            status.HTTP_201_CREATED,
        )