from rest_framework import serializers
from .models import (
    KYC,
    Passport,
    DrivingLicense,
    NationalID
)


class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = "__all__"
        read_only_fields = ["id", "user", "status", "created_at"]


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]


class DrivingLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrivingLicense
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]


class NationalIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalID
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]

class KYCResponseSerializer(serializers.Serializer):
    passport = PassportSerializer(required=False, allow_null=True)
    driving_license = DrivingLicenseSerializer(required=False, allow_null=True)
    national_id = NationalIDSerializer(required=False, allow_null=True)
    kyc_status = serializers.CharField()