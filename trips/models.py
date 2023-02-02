from datetime import timedelta
from django.utils.dateparse import parse_duration
import uuid
from django.db import models
from users.models import User_extension

# Create your models here.
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def soonest_for_user(self, user_extension):
        return self.get_queryset().filter(trip_owner=user_extension).order_by("")


class Duration_Bound(models.Model):
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    _default_time_delta = models.DurationField(default=timedelta(hours=4))

    @property
    def duration(self):
        if self.start_time is None or self.end_time is None:
            time_delta = self._default_time_delta
        else:
            time_delta = self.end_time - self.start_time
        self._default_time_delta = time_delta
        self.save()
        return time_delta

    class Meta:
        abstract = True


class Destination(models.Model):
    destination_name = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100, default="")
    destination_longitude = models.CharField(max_length=100, default="")
    destination_latitude = models.CharField(max_length=100, default="")
    _destination_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    # is_deleted = models.BooleanField(default=False)

    @property
    def destination_uuid(self):
        return str(self._destination_uuid)

    def summary(self):
        SUMMARY_FIELDS = [
            "destination_name",
            "destination_country",
            "destination_longitude",
            "destination_latitude",
            "destination_uuid",
            # "is_deleted",
        ]
        summary = {}
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        return summary

    def create_destination(destination):
        destination = Destination(
            destination_name=destination.name,
            destination_country=destination.country,
            destination_longitude=destination.lng,
            destination_latitude=destination.lat,
        )
        destination.save()
        return destination

    # objects = models.Manager()
    # active = ActiveManager()


class Base_Trip(models.Model):
    trip_name = models.CharField(max_length=100)
    trip_icon = models.CharField(max_length=100)
    trip_icon_color = models.CharField(max_length=100)
    trip_description = models.CharField(max_length=500, default="")
    trip_img = models.CharField(
        max_length=200, default="Some Location to Access Deafult Image"
    )
    num_people = models.IntegerField(null=True)
    destinations = models.ManyToManyField(Destination, related_name="destinations")
    public = models.BooleanField(default=False)
    _trip_uuid = models.UUIDField(default=uuid.uuid4)
    alert_time = models.DurationField(default=timedelta(days=1))
    is_deleted = models.BooleanField(default=False)
    trip_owner = models.ForeignKey(User_extension, on_delete=models.CASCADE)
    authorized_users = models.ManyToManyField(
        User_extension, related_name="authorized_users"
    )
    pending_permission = models.ManyToManyField(
        User_extension, related_name="pending_permission"
    )
    users_that_liked_trip = models.ManyToManyField(
        User_extension, related_name="Trips_User_liked"
    )
    users_that_starred_trip = models.ManyToManyField(
        User_extension, related_name="Trips_User_starred"
    )
    users_that_questioned_trip = models.ManyToManyField(
        User_extension, related_name="Trips_User_questioned"
    )

    @property
    def trip_uuid(self):
        return str(self._trip_uuid)

    objects = models.Manager()
    active = ActiveManager()

    def trip_summary(self):
        SUMMARY_FIELDS = [
            "trip_name",
            "trip_uuid",
            "trip_img",
            "trip_icon",
            "trip_icon_color",
            "num_people",
            "public",
            "alert_time",
            "is_deleted",
            "trip_description",
        ]
        summary = {}
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        summary["trip_owner"] = self.trip_owner.summary()
        summary["authorized_users"] = [
            au.summary() for au in self.authorized_users.all()
        ]
        return summary

    def trip_details(self):
        details = self.trip_summary()
        details["destinations"] = [d.summary() for d in self.destinations.filter()]
        details["authorized_users"] = [
            au.summary() for au in self.authorized_users.all()
        ]
        details["pending_permission"] = [
            ap.summary() for ap in self.pending_permission.all()
        ]
        details["users_that_liked_trip"] = [
            like.summary() for like in self.users_that_liked_trip.all()
        ]
        details["users_that_starred_trip"] = [
            star.summary() for star in self.users_that_starred_trip.all()
        ]
        details["users_that_questioned_trip"] = [
            question.summary() for question in self.users_that_questioned_trip.all()
        ]
        details["tags"] = [
            tag.summary() for tag in self.trip_tag_usages.filter(trip=self)
        ]
        details["events"] = [
            event.details() for event in self.events.filter(trip=self, is_deleted=False)
        ]
        return details

    def populate_values(self, data):
        trip_name = data["trip_name"]
        trip_img = data["trip_img"]
        num_people = data["num_people"]

        setattr(self, "trip_name", trip_name)
        setattr(self, "trip_img", trip_img)
        setattr(self, "num_people", num_people)

        if "public" in data:
            setattr(self, "public", data["public"])

        if "alert_time" in data:
            self.alert_time = parse_duration(data["alert_time"])

        self.save()
        return self


class Planned_trip(Base_Trip, Duration_Bound):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    _default_time_delta = models.DurationField(default=timedelta(days=7))

    def details(self):
        summary = super().trip_details()
        # summary["duration"] = self.duration
        summary["start_time"] = self.start_time
        summary["end_time"] = self.end_time
        return summary

    def summary(self):
        summary = super().trip_summary()
        # summary["duration"] = self.duration
        summary["start_time"] = self.start_time
        summary["end_time"] = self.end_time
        return summary


class Unplanned_trip(Base_Trip, Duration_Bound):
    _default_time_delta = models.DurationField(default=timedelta(days=7))

    def details(self):
        summary = super().trip_details()
        summary["duration"] = self._default_time_delta
        summary["start_time"] = self.start_time
        summary["end_time"] = self.end_time
        return summary

    def summary(self):
        summary = super().trip_summary()
        summary["duration"] = self._default_time_delta
        summary["start_time"] = self.start_time
        summary["end_time"] = self.end_time
        return summary
