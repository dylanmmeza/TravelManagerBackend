# Generated by Django 4.1 on 2023-01-13 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="base_trip",
            name="trip_description",
            field=models.CharField(default="", max_length=500),
        ),
    ]
