from rest_framework import serializers
from accounts.models import Profile, UserWallet


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user", "created_at"]


class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = "__all__"
        read_only_fields = ["user", "created_at"]



class SuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.JSONField()