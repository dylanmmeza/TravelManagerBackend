from import_export import resources
from .models import Destination


class MyModelResource(resources.ModelResource):
    class Meta:
        model = Destination
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ("id",)
