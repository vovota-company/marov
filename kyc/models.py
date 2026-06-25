from django.db import models
from accounts.models import User



class KYC(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="kyc"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.status}"


class Passport(models.Model):
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="kyc_passport"
    )  

    type = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=100)
    surname = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    personal_identity_number = models.CharField(max_length=100)
    sex = models.CharField(max_length=20)
    place_of_birth = models.CharField(max_length=255)
    date_of_issuance = models.DateField()
    date_of_expiry = models.DateField()
    issuing_authority = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="kyc/passports/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.passport_number


class DrivingLicense(models.Model):
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="kyc_driving_license"
    )

    country = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=255)
    residence_address = models.TextField()
    driving_licence_number = models.CharField(max_length=100)
    date_of_issuance = models.DateField()
    date_of_expiry = models.DateField()
    issuing_at = models.CharField(max_length=255)
    issuing_authority = models.CharField(max_length=255)
    card_number = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="kyc/driving_licenses/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.driving_licence_number


class NationalID(models.Model):
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="kyc_national_id"
    )

    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=255)
    mother = models.CharField(max_length=255)
    father = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    gender = models.CharField(max_length=50)
    marriage_status = models.CharField(max_length=100)
    nmifp = models.CharField(max_length=100)
    issuing_at = models.CharField(max_length=255)
    issuing_authority = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.surname}"