from django.contrib import admin

# Register your models here.
from .models import (
    Location,
    Base_event,
    Generic_activity,
    Planned_activity,
    Unplanned_activity,
    Air_travel,
    Car_travel,
    Lodging,
)

admin.site.register(Location)
# admin.site.register(Base_event)
admin.site.register(Generic_activity)
admin.site.register(Planned_activity)
admin.site.register(Unplanned_activity)
admin.site.register(Air_travel)
admin.site.register(Car_travel)
admin.site.register(Lodging)
