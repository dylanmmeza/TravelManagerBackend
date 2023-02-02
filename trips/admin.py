from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import MyModelResource

# Register your models here.
from .models import Destination, Base_Trip, Planned_trip, Unplanned_trip

# admin.site.register(Destination)
admin.site.register(Base_Trip)
admin.site.register(Planned_trip)
admin.site.register(Unplanned_trip)


@admin.register(Destination)
class MyModelAdmin(ImportExportModelAdmin):
    resource_class = MyModelResource
