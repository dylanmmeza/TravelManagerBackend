# Generated by Django 4.1 on 2023-01-21 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0004_remove_destination_user_added_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="destination",
            name="is_deleted",
        ),
    ]
