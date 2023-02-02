from cgi import test
from django.db import models
import uuid

from events.models import Base_event
from users.models import User_extension
from trips.models import Base_Trip


class TagManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


# Create your models here.
class BaseTag(models.Model):
    tag_left = models.CharField(max_length=50)
    tag_right = models.CharField(max_length=50)
    _tag_uuid = models.UUIDField(default=uuid.uuid4)
    description = models.CharField(max_length=250, blank=True)

    @property
    def tag_uuid(self):
        return str(self._tag_uuid)

    # active = TagManager()
    objects = models.Manager()

    def summary(self):
        SUMMARY_FIELDS = ["tag_left", "tag_right", "description"]
        summary = {}
        summary["tag_uuid"] = self._tag_uuid
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        return summary

    def populate_values(self, data):
        setattr(self, "tag_left", data["tag_left"])
        setattr(self, "tag_right", data["tag_right"])
        if "description" in data:
            setattr(self, "description", data["description"])
        self.save()
        return self


class TripTag(BaseTag):
    used_by_trips = models.ManyToManyField(
        Base_Trip, through="TripTagUsage", related_name="trip_tags"
    )

    def summary(self):
        summary = super().summary()
        return summary


class TripTagUsage(models.Model):
    trip_tag = models.ForeignKey(TripTag, on_delete=models.CASCADE)
    trip = models.ForeignKey(
        Base_Trip, on_delete=models.CASCADE, related_name="trip_tag_usages"
    )
    confidence_interval_lb = models.FloatField(default=0.4)
    confidence_interval_ub = models.FloatField(default=0.6)
    value = models.FloatField(default=0.5)
    tag_creator = models.ForeignKey(
        User_extension, on_delete=models.CASCADE, related_name="trip_tag_creator"
    )
    last_updated_by = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="trip_tag_last_updated_by",
    )
    is_active = models.BooleanField(default=False)

    def summary(self):
        summary = {}
        summary = self.trip_tag.summary()
        summary["value"] = self.value
        summary["tag_creator"] = self.tag_creator.user_uuid
        summary["last_updated_by"] = self.last_updated_by.user_uuid
        summary["is_active"] = self.is_active
        return summary


class EventTag(BaseTag):
    used_by_events = models.ManyToManyField(
        Base_event, through="EventTagUsage", related_name="event_tags"
    )

    def summary(self):
        summary = super().summary()
        return summary


class EventTagUsage(models.Model):
    event_tag = models.ForeignKey(EventTag, on_delete=models.CASCADE)
    event = models.ForeignKey(
        Base_event, on_delete=models.CASCADE, related_name="event_tag_usages"
    )
    confidence_interval_lb = models.FloatField(default=0.4)
    confidence_interval_ub = models.FloatField(default=0.6)
    value = models.FloatField(default=0.5)
    tag_creator = models.ForeignKey(
        User_extension, on_delete=models.CASCADE, related_name="event_tag_creator"
    )
    last_updated_by = models.ForeignKey(
        User_extension,
        on_delete=models.CASCADE,
        related_name="event_tag_last_update_by",
    )
    is_active = models.BooleanField(default=False)

    def summary(self):
        summary = {}
        summary = self.event_tag.summary()
        summary["value"] = self.value
        summary["tag_creator"] = self.tag_creator.user_uuid
        summary["last_updated_by"] = self.last_updated_by.user_uuid
        summary["is_active"] = self.is_active
        return summary
