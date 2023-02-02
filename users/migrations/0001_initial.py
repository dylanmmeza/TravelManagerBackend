# Generated by Django 4.1 on 2023-01-03 23:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="User_extension",
            fields=[
                (
                    "date_of_birth",
                    models.DateField(default=django.utils.timezone.now, null=True),
                ),
                (
                    "_user_uuid",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("is_deleted", models.BooleanField(default=False)),
                ("bio", models.CharField(default="", max_length=350, null=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("my_friends", models.ManyToManyField(to="users.user_extension")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]