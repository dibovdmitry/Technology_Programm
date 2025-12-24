from import_export import resources
from .models import StudentGroup


class EmployeeResource(resources.ModelResource):
    class Meta:
        model = StudentGroup
