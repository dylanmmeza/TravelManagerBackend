from django.db import models
from datetime import timedelta
from events.models import Base_event
from trips.models import Base_Trip
from users.models import User_extension

import uuid

# Create your models here.


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Time_to_send(models.Model):
    start_time = models.DateTimeField()
    alert_time = models.DurationField(default=timedelta(hours=1))

    @property
    def time_calculation(self):
        if self.start_time is not None and self.alert_time is not None:
            time_to_send = self.start_time - self.alert_time
        else:
            time_to_send = None
        return time_to_send

    class Meta:
        abstract = True


class Base_notification(models.Model):
    is_active = models.BooleanField(default=True)
    main_icon = models.CharField(default="default", max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    _notification_uuid = models.UUIDField(default=uuid.uuid4)

    @property
    def notification_uuid(self):
        return str(self._notification_uuid)

    def summary(self):
        SUMMARY_FIELDS = ["is_active", "main_icon", "timestamp", "notification_uuid"]
        summary = {}
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        return summary

    def populate_values(self, data):
        POPULATE_FIELDS = ["is_active", "main_icon"]
        for field in POPULATE_FIELDS:
            if field in data:
                setattr(self, field, data[field])
        self.save()
        return self

    objects = models.Manager()
    active = ActiveManager()


class Event_alert(Base_notification, Time_to_send):
    event = models.ForeignKey(Base_event, on_delete=models.CASCADE)
    recieving_user = models.ForeignKey(
        User_extension, on_delete=models.CASCADE, related_name="trip_alerts"
    )

    @property
    def start_time(self):
        event = self.event
        if hasattr(event, "generic_activity"):
            activity = event.generic_activity
            if hasattr(activity, "planned_activity"):
                return activity.planned_activity.start_time
            elif hasattr(activity, "unplanned_activity"):
                return activity.unplanned_activity.start_time
            else:
                pass
        elif hasattr(event, "air_travel"):
            return event.air_travel.start_time
        elif hasattr(event, "car_travel"):
            return event.car_travel.start_time
        elif hasattr(event, "lodging"):
            return event.lodging.start_time
        else:
            pass

    @property
    def alert_time(self):
        return self.event.alert_time

    def summary(self):
        summary = super().summary()
        summary["start_time"] = self.start_time
        summary["time_to_send"] = self.time_calculation
        summary["event"] = self.event.summary()
        summary["recieving_user"] = self.recieving_user.summary()
        return summary


class Trip_Time_Alert(Base_notification, Time_to_send):
    trip = models.ForeignKey(Base_Trip, on_delete=models.CASCADE)
    recieving_user = models.ForeignKey(
        User_extension, on_delete=models.CASCADE, related_name="trip_alert"
    )

    @property
    def start_time(self):
        if hasattr(self.trip, "planned_trip"):
            return self.trip.planned_trip.start_time
        elif hasattr(self.trip, "unplanned_trip"):
            return self.trip.unplanned_trip.start_time

    @property
    def alert_time(self):
        return self.trip.alert_time

    def summary(self):
        summary = super().summary()
        summary["trip"] = self.trip.summary()
        summary["recieving_user"] = self.recieving_user.summary()
        summary["start_time"] = self.start_time
        summary["time_to_send"] = self.time_calculation
        return summary


class Friend_request(Base_notification, Time_to_send):
    sending_user = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="sending_user_friend_request",
    )
    recieving_user = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="recieving_user_friend_request",
    )
    start_time = models.DateTimeField(auto_now_add=True)
    alert_time = models.DurationField(default=timedelta(minutes=-5))

    def summary(self):
        summary = super().summary()
        summary["sending_user"] = self.sending_user.summary()
        summary["recieving_user"] = self.recieving_user.summary()
        summary["time_to_send"] = self.time_calculation
        return summary


class Trip_request(Base_notification, Time_to_send):
    trip = models.ForeignKey(
        Base_Trip, on_delete=models.CASCADE, related_name="trip_requests"
    )
    sending_user = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="sending_user_trip_request",
    )
    recieving_user = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="recieving_user_trip_request",
    )
    start_time = models.DateTimeField(auto_now_add=True)
    alert_time = models.DurationField(default=timedelta(minutes=-5))

    def summary(self):
        summary = super().summary()
        summary["trip"] = self.trip.summary()
        summary["sending_user"] = self.sending_user.summary()
        summary["recieving_user"] = self.recieving_user.summary()
        summary["time_to_send"] = self.time_calculation
        return summary


class General_Trip_Notification(Base_notification, Time_to_send):
    CHOICES = [(1, "Trip Change"), (2, "Friend Trip Created")]
    trip = models.ForeignKey(
        Base_Trip, on_delete=models.CASCADE, related_name="general_trip_notification"
    )
    sending_user = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="sending_user_general_trip_request",
    )
    recieving_user = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="recieving_user_general_trip_request",
    )
    start_time = models.DateTimeField(auto_now_add=True)
    alert_time = models.DurationField(default=timedelta(minutes=-5))
    notification_type = models.IntegerField()
    # Can add type and get rid of trip related notification (1=Trip Change, 2=Friend Trip Created)

    def summary(self):
        summary = super().summary()
        summary["trip"] = self.trip.summary()
        summary["sending_user"] = self.sending_user.summary()
        summary["recieving_user"] = self.recieving_user.summary()
        summary["time_to_send"] = self.time_calculation
        summary["notification_type"] = self.notification_type
        return summary
