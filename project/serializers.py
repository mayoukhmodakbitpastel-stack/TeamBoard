from rest_framework import serializers
from .models import Project , ProjectMember
from employee.models import Employee
from employee.md5_hash import md5_decode_id as md5_decode_employee_id, md5_hash_id as md5_hash_employee_id
from .md5_hash import md5_hash_message_id, md5_hash_project_id, md5_decode_project_id

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

class ProjectMemberSerializer(serializers.ModelSerializer):
    project_id = serializers.CharField()
    member_id = serializers.CharField()
    id = serializers.SerializerMethodField()
    member_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'project_id', 'member_id', 'is_admin', 'member_name']

    def get_id(self, obj):
        return md5_hash_employee_id(obj.id)

    def get_member_name(self, obj):
        return obj.member.first_name if obj.member else None

    def validate(self, attrs):
        project_decoded = md5_decode_project_id(attrs['project_id'], Project)
        member_decoded = md5_decode_employee_id(attrs['member_id'], Employee)

        if not project_decoded or not member_decoded:
            raise serializers.ValidationError("Invalid Project or Member ID.")

        try:
            attrs['project'] = Project.objects.get(id=project_decoded, status='1')
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found or inactive.")

        try:
            attrs['member'] = Employee.objects.get(id=member_decoded, status='1')
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found or inactive.")

        return attrs

    def create(self, validated_data):
        validated_data.pop('project_id', None)
        validated_data.pop('member_id', None)
        return super().create(validated_data)

    def to_representation(self, instance):
        # get the default representation
        data = super().to_representation(instance)

        # override project_id and member_id with hashed IDs
        data['project_id'] = md5_hash_project_id(instance.project.id) if instance.project else None
        data['member_id'] = md5_hash_employee_id(instance.member.id) if instance.member else None

        return data
    