from rest_framework import serializers
from .models import Project , ProjectMember, ProjectMessage
from employee.models import Employee
from employee.md5_hash import md5_decode_id as md5_decode_employee_id, md5_hash_id as md5_hash_employee_id
from .md5_hash import md5_hash_message_id, md5_hash_project_id, md5_decode_project_id

# Serializer for Project Messages

class ProjectMessageSerializer(serializers.ModelSerializer):
    project_id = serializers.CharField(write_only=True)
    sender_id = serializers.CharField(write_only=True)

    id = serializers.SerializerMethodField(read_only=True)
    project = serializers.SerializerMethodField(read_only=True)
    sender = serializers.SerializerMethodField(read_only=True)

    # Make text_body and media_url optional
    text_body = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    media_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ProjectMessage
        fields = [
            'id',
            'project_id',
            'sender_id',
            'project',
            'sender',
            'text_body',
            'has_media',
            'media_url',
            'system_creation_time'
        ]
        read_only_fields = ['has_media', 'system_creation_time']

    def get_id(self, obj):
        return md5_hash_message_id(obj.id)

    def get_project(self, obj):
        return {
            "id": md5_hash_project_id(obj.project.id),
            "title": obj.project.title
        } if obj.project else None

    def get_sender(self, obj):
        return {
            "id": md5_hash_employee_id(obj.sender.id),
            "first_name": obj.sender.first_name
        } if obj.sender else None

    def validate(self, attrs):
        # Decode hashed IDs
        project_decoded = md5_decode_project_id(attrs['project_id'], Project)
        sender_decoded = md5_decode_employee_id(attrs['sender_id'], Employee)

        if not project_decoded or not sender_decoded:
            raise serializers.ValidationError("Invalid Project or Sender ID.")

        # Validate project and employee status
        try:
            attrs['project'] = Project.objects.get(id=project_decoded, status='1')
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found or inactive.")

        try:
            attrs['sender'] = Employee.objects.get(id=sender_decoded, status='1')
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found or inactive.")

        # Ensure at least one of text_body or media_url is provided
        text_body = attrs.get('text_body')
        media_url = attrs.get('media_url')
        if not text_body and not media_url:
            raise serializers.ValidationError("Either text_body or media_url must be provided.")

        # Automatically set has_media based on media_url
        attrs['has_media'] = bool(media_url)

        # Clean up write-only fields
        attrs.pop('project_id')
        attrs.pop('sender_id')

        return attrs
