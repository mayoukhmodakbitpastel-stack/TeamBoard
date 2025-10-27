from django.shortcuts import render

# Create your views here.
from .models import ProjectMessage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as drf_status
from django.core.paginator import Paginator
from .serializers import ProjectMessageSerializer
from employee.models import Employee
from project.serializers import ProjectSerializer, ProjectMemberSerializer
from project.models import Project,ProjectMember
from .md5_hash import md5_hash_project_id, md5_decode_project_id
from employee.md5_hash import md5_hash_id as md5_hash_employee_id, md5_decode_id as md5_decode_employee_id

@api_view(['POST'])
def create_message(request):
    serializer = ProjectMessageSerializer(data=request.data)
    if serializer.is_valid():
        project = serializer.validated_data.get('project')
        sender_emp = serializer.validated_data.get('sender')

        # check if sender is a member of the project
        membership = ProjectMember.objects.filter(
            project=project,
            member=sender_emp,
            status='1'
        ).first()
        if not membership:
            return Response({
                "status": "error",
                "message": "Sender is not a member of the project",
                "data": {}
            }, status=400)

        # check if sender is active employee
        if not sender_emp:
            return Response({
                "status": "error",
                "message": "Sender employee is inactive or does not exist",
                "data": {}
            }, status=400)

        # check if project is active
        if not project:
            return Response({
                "status": "error",
                "message": "Project is inactive or does not exist",
                "data": {}
            }, status=400)

        # check that at least one of text_body or media_url is provided
        text_body = serializer.validated_data.get('text_body')
        media_url = serializer.validated_data.get('media_url')

        if not text_body and not media_url:
            return Response({
                "status": "error",
                "message": "Either text_body or media_url must be provided",
                "data": {}
            }, status=400)

        # determine has_media automatically based on media_url existence
        serializer.validated_data['has_media'] = bool(media_url)

        # save message
        message = serializer.save()
        return Response({
            "status": "OK",
            "message": "Message posted successfully",
            "data": ProjectMessageSerializer(message).data
        }, status=drf_status.HTTP_201_CREATED)

    return Response({
        "status": "error",
        "message": "Validation failed",
        "data": serializer.errors
    }, status=400)


# List Project Messages
@api_view(['POST'])
def list_project_messages(request):
    project_id = request.data.get('project_id')
    limit = int(request.data.get('limit'))
    page = int(request.data.get('page'))

    # messages = ProjectMessage.objects.filter(status='1').order_by('-system_creation_time') #only for active member msg
    messages = ProjectMessage.objects.all().order_by('-system_creation_time') #all msgs
    status_filter = request.data.get('status')
    if project_id:
        decoded_proj = md5_decode_project_id(project_id, Project)
        messages = messages.filter(project_id=decoded_proj)
    if status_filter:
        messages = messages.filter(status=status_filter)
    # paginator = Paginator(messages, limit)
    # page_obj = paginator.get_page(page)
    
    # Apply pagination only if both limit and page are valid integers
    try:
        limit = int(limit) if limit is not None else None
        page = int(page) if page is not None else None
    except ValueError:
        return Response({
            "Status": "ERROR",
            "Message": "Limit and page must be integers.",
            "Data": {}
        }, status=drf_status.HTTP_400_BAD_REQUEST)

    if limit is not None and page is not None:
        if limit <= 0 or page <= 0:
            return Response({
                "Status": "ERROR",
                "Message": "Limit and page must be positive integers.",
                "Data": {}
            }, status=drf_status.HTTP_400_BAD_REQUEST)
            

        # Calculate start and end indices for slicing
        start = (page - 1) * limit
        end = start + limit
        messages = messages[start:end]

    serialized = ProjectMessageSerializer(messages, many=True).data
    return Response({
        "status": "OK",
        "message": "Messages retrieved successfully",
        "data": serialized
    })


# List Employee Messages
@api_view(['POST'])
def list_employee_messages(request):
    member_id = request.data.get('member_id')
    limit = int(request.data.get('limit', 10))
    page = int(request.data.get('page', 1))

    messages = ProjectMessage.objects.filter(status='1').order_by('-system_creation_time')
    if member_id:
        decoded_emp = md5_decode_employee_id(member_id, Employee)
        messages = messages.filter(sender_id=decoded_emp)

    paginator = Paginator(messages, limit)
    page_obj = paginator.get_page(page)

    serialized = ProjectMessageSerializer(page_obj, many=True).data
    return Response({
        "status": "OK",
        "message": "Messages retrieved successfully",
        "data": serialized
    })
