from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .models import Chat
from .serializers import ChatSerializer

from drf_spectacular.utils import extend_schema_view, extend_schema


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

@extend_schema_view(
    create=extend_schema(request=ChatSerializer, responses=ChatSerializer, tags=["Chat"]),
    list=extend_schema(responses=ChatSerializer(many=True), tags=["Chat"]),
    retrieve=extend_schema(responses=ChatSerializer(many=True), tags=["Chat"]),
)
class ChatViewSet(CustomResponseMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # -------------------------
    # SEND MESSAGE
    # -------------------------
    
    def create(self, request):
        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(sender=request.user)

        return self.success(
            serializer.data,
            "Message sent",
            status.HTTP_201_CREATED
        )

    # -------------------------
    # LIST CONVERSATIONS (FRIENDS)
    # -------------------------
    def list(self, request):
        user = request.user

        chats = Chat.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by("-created_at")

        friends = set()

        for c in chats:
            if c.sender == user:
                friends.add(c.receiver)
            else:
                friends.add(c.sender)

        data = [
            {
                "id": f.id,
                "username": f.username,
                "email": f.email,
            }
            for f in friends
        ]

        return self.success(
            data=data,
            message="Conversation list fetched"
        )

    # -------------------------
    # SINGLE CONVERSATION MESSAGES
    # -------------------------
    def retrieve(self, request, pk=None):
        user = request.user

        messages = Chat.objects.filter(
            Q(sender=user, receiver_id=pk) |
            Q(sender_id=pk, receiver=user)
        ).order_by("created_at")

        return self.success(
            ChatSerializer(messages, many=True).data,
            "Conversation messages fetched"
        )