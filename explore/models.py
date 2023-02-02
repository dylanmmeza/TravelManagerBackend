from django.db import models
import uuid

from travel_manager.trips.models import Base_Trip


# Create your models here.
class Post(models.Model):
    post_uuid = models.UUIDField(default=uuid.uuid4)
    is_deleted = models.BooleanField(default=False)
    trip = models.ForeignKey(Base_Trip, on_delete=models.CASCADE)

    @property
    def post_uuid(self):
        return str(self.post_uuid)
