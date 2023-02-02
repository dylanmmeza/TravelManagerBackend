from django.db import models
from django.utils.dateparse import parse_duration
import uuid
from datetime import timedelta
from trips.models import Base_Trip, Destination, Duration_Bound


from users.models import User_extension

# Create your models here.


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Location(models.Model):
    place_id = models.CharField(max_length=100)
    Json_location = models.JSONField(null=True)
    formatted_address = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=100, null=True)
    icon = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    opening_hours = models.JSONField(null=True)
    photos = models.CharField(max_length=200, null=True)
    # API returns 10 so  will have to store only 1
    price_level = models.IntegerField(null=True)
    rating = models.IntegerField(null=True)
    website = models.CharField(max_length=100, null=True)

    def populate_values(self, data):
        FIELDS = [
            "place_id",
            "Json_location",
            "formatted_address",
            "phone_number",
            "phone_number",
            "icon",
            "name",
            "opening_hours",
            "photos",
            "price_level",
            "rating",
            "website",
        ]
        for field in FIELDS:
            if field in data:
                setattr(self, field, data[field])
        self.save()
        return self

    def summary(self):
        summary = {}
        FIELDS = [
            "place_id",
            "Json_location",
            "formatted_address",
            "phone_number",
            "phone_number",
            "icon",
            "name",
            "opening_hours",
            "photos",
            "price_level",
            "rating",
            "website",
        ]
        for field in FIELDS:
            summary[field] = getattr(self, field)
        return summary


class Base_event(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    user_added = models.ForeignKey(
        User_extension, on_delete=models.CASCADE, related_name="Base_event"
    )
    notes = models.CharField(max_length=500, null=True)
    alert_time = models.DurationField(default=timedelta(hours=1))
    is_deleted = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    _event_uuid = models.UUIDField(default=uuid.uuid4)
    trip = models.ForeignKey(Base_Trip, on_delete=models.CASCADE, related_name="events")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, null=True)

    objects = models.Manager()
    active = ActiveManager()

    @property
    def event_uuid(self):
        return str(self._event_uuid)

    def summary(self):
        SUMMARY_FIELDS = [
            "name",
            "category",
            "notes",
            "alert_time",
            "is_deleted",
            "locked",
            "event_uuid",
            "is_deleted",
        ]
        summary = {}
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        summary["user_added"] = self.user_added._user_uuid
        summary["trip"] = self.trip._trip_uuid
        if self.destination is not None:
            summary["destination"] = self.destination._destination_uuid
        return summary

    def details(self):
        details = self.summary()

        details["tags"] = [
            tag.summary() for tag in self.event_tags.filter(eventtagusage__event=self)
        ]
        return details

    def populate_values(self, data):
        if "trip_uuid" in data:
            trip_uuid = data["trip_uuid"]
            trip = Base_Trip.active.get(_trip_uuid=trip_uuid)
            setattr(self, "trip", trip)

        FIELDS = ["name", "category", "notes", "locked"]

        for field in FIELDS:
            if field in data:
                setattr(self, field, data[field])

        if "destination_uuid" in data:
            destination_uuid = data["destination_uuid"]
            destination = trip.destinations.active.get(
                _destination_uuid=destination_uuid
            )
            setattr(self, "destination", destination)

        if "alert_time" in data:
            self.alert_time = parse_duration(data["alert_time"])

        self.save()
        return self


class Generic_activity(Base_event):
    num_people = models.IntegerField(null=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="generic_activity", null=True
    )
    image = models.CharField(max_length=200, default="")  # add location

    def summary(self):
        SUMMARY_FIELDS = [
            "num_people",
            "image",
        ]
        summary = super().summary()
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        summary["location"] = self.location
        return summary

    def populate_values(self, data, user_extension):
        super().populate_values(data)
        FIELDS = ["num_people", "image"]

        for field in FIELDS:
            if field in data:
                setattr(self, field, data[field])

        if "place_id" in data:
            self.location = Location.active.get(place_id=data["place_id"])

        self.save()
        return self


class Planned_activity(Generic_activity, Duration_Bound):
    _default_time_delta = models.DurationField(default=timedelta(hours=1))
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    locked = True

    def summary(self):
        summary = super().summary()
        summary["duration"] = self.duration
        summary["start_time"] = self.start_time
        summary["end_time"] = self.end_time
        return summary


class Unplanned_activity(Generic_activity, Duration_Bound):
    _default_time_delta = models.DurationField(default=timedelta(hours=1))

    def summary(self):
        summary = super().summary()
        summary["duration"] = self._default_time_delta
        return summary


class Air_travel(Base_event, Duration_Bound):
    flight_number = models.CharField(max_length=10, null=True)
    flight_origin = models.CharField(max_length=100)
    flight_destination = models.CharField(max_length=100)
    confirmation = models.CharField(max_length=50, null=True)

    def summary(self):
        summary = super().summary()
        SUMMARY_FIELDS = [
            "flight_number",
            "flight_origin",
            "flight_destination",
            "start_time",
            "end_time",
            "duration",
        ]
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)
        return summary


class Car_travel(Base_event, Duration_Bound):
    starting_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="car_travel_start"
    )
    ending_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="car_travel_end"
    )
    confirmation = models.CharField(max_length=50, null=True)

    def summary(self):
        summary = super().summary()
        SUMMARY_FIELDS = [
            "confirmation",
            "start_time",
            "end_time",
            "duration",
        ]
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)

        summary["starting_location"] = self.starting_location.summary()
        summary["ending_location"] = self.ending_location.summary()
        return summary


class Lodging(Base_event, Duration_Bound):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="Lodging"
    )
    confirmation = models.CharField(max_length=50, null=True)
    _default_time_delta = models.DurationField(default=timedelta(days=1))

    def summary(self):
        summary = super().summary()
        SUMMARY_FIELDS = [
            "confirmation",
            "start_time",
            "end_time",
            "duration",
        ]
        for field in SUMMARY_FIELDS:
            summary[field] = getattr(self, field)

        summary["location"] = self.location.summary()
        return summary
