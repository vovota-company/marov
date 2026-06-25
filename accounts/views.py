from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

User = get_user_model()


@extend_schema(
    request={
        "type": "object",
        "properties": {
            "id_token": {"type": "string"}
        }
    },
    responses=200
)
class GoogleLoginView(APIView):

    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response(
                {"error": "id_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 🔐 Verify Google token
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request()
            )

            email = idinfo.get("email")
            name = idinfo.get("name", "")
            picture = idinfo.get("picture", "")
            given_name = idinfo.get("given_name", "")
            family_name = idinfo.get("family_name", "")
            google_id = idinfo.get("sub")
            email_verified = idinfo.get("email_verified", False)

            if not email:
                return Response(
                    {"error": "Google account has no email"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 👤 Create or update user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email.split("@")[0],
                    "google_id": google_id,
                    "avatar": picture,
                    "email_verified": email_verified,
                }
            )

            # 🔁 Always update latest Google data
            user.google_id = google_id
            user.avatar = picture
            user.email_verified = email_verified

            if given_name:
                user.first_name = given_name
            if family_name:
                user.last_name = family_name

            user.save()

            # 🧾 Update profile safely
            profile = user.profile
            profile.full_name = name
            profile.avatar = picture
            profile.given_name = given_name
            profile.family_name = family_name
            profile.save()

            # 🔑 JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "name": name,
                    "avatar": picture,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })

        except Exception as e:
            return Response(
                {"error": "Invalid Google token", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )