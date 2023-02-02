from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import uuid
from django.utils import timezone


# Create your models here.
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class User_extension(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    date_of_birth = models.DateField(null=True, default=timezone.now)
    _user_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    is_deleted = models.BooleanField(default=False)
    my_friends = models.ManyToManyField("self")
    bio = models.CharField(default="", null=True, max_length=350)
    updated = models.DateTimeField(auto_now=True)
    profile_picture = models.CharField(
        max_length=200, default="Some Location to Access Deafult Image"
    )

    @property
    def user_uuid(self):
        return str(self._user_uuid)

    objects = models.Manager()
    active = ActiveManager()

    def summary(self):
        summary = {}
        BASE_SUMMARY_FIELDS = [
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
        ]
        for base_field in BASE_SUMMARY_FIELDS:
            summary[base_field] = getattr(self.user, base_field)

        SUMMARY_FIELDS = [
            "date_of_birth",
            "_user_uuid",
            "is_deleted",
            "bio",
            "updated",
            "profile_picture",
        ]
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        return summary

    def user_details(self):
        details = self.summary()
        details["my_friends"] = [f.summary() for f in self.my_friends.all()]
        return details

    def create_user(data):
        username = data["username"]
        password = data["password"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        date_of_birth = data["date_of_birth"]
        if "bio" in data:
            bio = data["bio"]
        else:
            bio = None
        email = data["email"]

        base_user = User(
            username=username,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        base_user.save()
        user = User_extension(user=base_user, date_of_birth=date_of_birth, bio=bio)
        user.save()

        return user
