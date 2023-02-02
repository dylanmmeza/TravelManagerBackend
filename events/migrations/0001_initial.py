# Generated by Django 4.1 on 2023-01-03 23:13

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("trips", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Base_event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("category", models.CharField(max_length=100)),
                ("notes", models.CharField(max_length=500, null=True)),
                (
                    "alert_time",
                    models.DurationField(default=datetime.timedelta(seconds=3600)),
                ),
                ("is_deleted", models.BooleanField(default=False)),
                ("locked", models.BooleanField(default=False)),
                ("_event_uuid", models.UUIDField(default=uuid.uuid4)),
                (
                    "destination",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="trips.destination",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="trips.base_trip",
                    ),
                ),
                (
                    "user_added",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Base_event",
                        to="users.user_extension",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("place_id", models.CharField(max_length=100)),
                ("Json_location", models.JSONField(null=True)),
                ("formatted_address", models.CharField(max_length=200, null=True)),
                ("phone_number", models.CharField(max_length=100, null=True)),
                ("icon", models.CharField(max_length=100, null=True)),
                ("name", models.CharField(max_length=100, null=True)),
                ("opening_hours", models.JSONField(null=True)),
                ("photos", models.CharField(max_length=200, null=True)),
                ("price_level", models.IntegerField(null=True)),
                ("rating", models.IntegerField(null=True)),
                ("website", models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Air_travel",
            fields=[
                (
                    "base_event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="events.base_event",
                    ),
                ),
                ("start_time", models.DateTimeField(null=True)),
                ("end_time", models.DateTimeField(null=True)),
                (
                    "_default_time_delta",
                    models.DurationField(default=datetime.timedelta(seconds=14400)),
                ),
                ("flight_number", models.CharField(max_length=10, null=True)),
                ("flight_origin", models.CharField(max_length=100)),
                ("flight_destination", models.CharField(max_length=100)),
                ("confirmation", models.CharField(max_length=50, null=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("events.base_event", models.Model),
        ),
        migrations.CreateModel(
            name="Generic_activity",
            fields=[
                (
                    "base_event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="events.base_event",
                    ),
                ),
                ("num_people", models.IntegerField(null=True)),
                ("image", models.CharField(default="", max_length=200)),
                (
                    "location",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="generic_activity",
                        to="events.location",
                    ),
                ),
            ],
            bases=("events.base_event",),
        ),
        migrations.CreateModel(
            name="Planned_activity",
            fields=[
                (
                    "generic_activity_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="events.generic_activity",
                    ),
                ),
                (
                    "_default_time_delta",
                    models.DurationField(default=datetime.timedelta(seconds=3600)),
                ),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
            ],
            options={
                "abstract": False,
            },
            bases=("events.generic_activity", models.Model),
        ),
        migrations.CreateModel(
            name="Unplanned_activity",
            fields=[
                (
                    "generic_activity_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="events.generic_activity",
                    ),
                ),
                ("start_time", models.DateTimeField(null=True)),
                ("end_time", models.DateTimeField(null=True)),
                (
                    "_default_time_delta",
                    models.DurationField(default=datetime.timedelta(seconds=3600)),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("events.generic_activity", models.Model),
        ),
        migrations.CreateModel(
            name="Lodging",
            fields=[
                (
                    "base_event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="events.base_event",
                    ),
                ),
                ("start_time", models.DateTimeField(null=True)),
                ("end_time", models.DateTimeField(null=True)),
                ("confirmation", models.CharField(max_length=50, null=True)),
                (
                    "_default_time_delta",
                    models.DurationField(default=datetime.timedelta(days=1)),
                ),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Lodging",
                        to="events.location",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("events.base_event", models.Model),
        ),
        migrations.CreateModel(
            name="Car_travel",
            fields=[
                (
                    "base_event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="events.base_event",
                    ),
                ),
                ("start_time", models.DateTimeField(null=True)),
                ("end_time", models.DateTimeField(null=True)),
                (
                    "_default_time_delta",
                    models.DurationField(default=datetime.timedelta(seconds=14400)),
                ),
                ("confirmation", models.CharField(max_length=50, null=True)),
                (
                    "ending_location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="car_travel_end",
                        to="events.location",
                    ),
                ),
                (
                    "starting_location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="car_travel_start",
                        to="events.location",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("events.base_event", models.Model),
        ),
    ]
