# Generated by Django 4.1 on 2023-01-12 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user_extension",
            name="profile_picture",
            field=models.CharField(
                default="Some Location to Access Deafult Image", max_length=200
            ),
        ),
    ]
