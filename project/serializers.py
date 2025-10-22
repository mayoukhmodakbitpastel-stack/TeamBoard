from rest_framework import serializers
from .models import Project
from employee.models import Employee
from employee.md5_hash import md5_decode_id as md5_decode_employee_id, md5_hash_id as md5_hash_employee_id
from .md5_hash import md5_hash_project_id, md5_decode_project_id

class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()  # hashed project ID
    created_by = serializers.CharField(write_only=True)  # hashed employee ID input
    created_by_emp = serializers.SerializerMethodField(read_only=True)  # hashed employee ID output

    class Meta:
        model = Project
        fields = [
            'id',                # hashed project id (output only)
            'title',
            'description',
            'banner_image_url',
            'created_by',        # hashed employee id (write-only input)
            'created_by_emp',   # hashed employee id (read-only output)
            'status',
            'system_creation_time',
        ]
        extra_kwargs = {
            'status': {'required': False},
            'system_creation_time': {'required': False},
            'system_update_time': {'required': False},
        }

    def get_id(self, obj):
        return md5_hash_project_id(obj.id)

    def get_created_by_emp(self, obj):
        if obj.created_by:
            return md5_hash_employee_id(obj.created_by.id)
        return None

    def validate_created_by(self, value):
        employee_id = md5_decode_employee_id(value, Employee)
        if not employee_id:
            raise serializers.ValidationError("Invalid hashed Employee ID.")
        try:
            return Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found.")

    def create(self, validated_data):
        # At this point, validate_created_by has returned an Employee instance
        validated_data['created_by'] = self.validated_data['created_by']

        if 'status' not in validated_data or not validated_data['status']:
            validated_data['status'] = '1'

        if 'system_creation_time' not in validated_data:
            from django.utils.timezone import now
            validated_data['system_creation_time'] = now()

        return super().create(validated_data)
