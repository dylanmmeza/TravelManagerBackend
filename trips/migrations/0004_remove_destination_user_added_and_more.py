# Generated by Django 4.1 on 2023-01-17 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0003_destination_destination_latitude_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="destination",
            name="user_added",
        ),
        migrations.AddField(
            model_name="destination",
            name="destination_country",
            field=models.CharField(default="", max_length=100),
        ),
    ]
