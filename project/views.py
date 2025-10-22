from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as drf_status
from .serializers import ProjectSerializer
from .models import Project
from .md5_hash import md5_hash_project_id, md5_decode_project_id
from employee.md5_hash import md5_hash_id as md5_hash_employee_id, md5_decode_id as md5_decode_employee_id

@api_view(['POST'])
def create_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        project = serializer.save()
        response_data = ProjectSerializer(project).data
        return Response({
            "status": "OK",
            "message": "Project created successfully",
            "data": response_data
        }, status=drf_status.HTTP_201_CREATED)
    
    return Response({
        "status": "error",
        "message": "Validation failed",
        "data": serializer.errors
    }, status=drf_status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def get_project_details(request):
    project_id = request.data.get('id')
    if not project_id:
        return Response({"status": "error", "message": "Missing 'id'", "data": {}}, status=400)

    if str(project_id).isdigit():
        project = Project.objects.filter(id=project_id, status='1').first()
    else:
        decoded_id = md5_decode_project_id(project_id, Project)
        project = Project.objects.filter(id=decoded_id, status='1').first()

    if not project:
        return Response({"status": "error", "message": "Project not found", "data": {}}, status=404)

    from .serializers import ProjectSerializer
    data = ProjectSerializer(project).data

    return Response({
        "status": "OK",
        "message": "Project details retrieved successfully",
        "data": data
    }, status=200)
@api_view(['POST'])
def list_projects(request):
    from django.core.paginator import Paginator
    from .models import Project
    from .serializers import ProjectSerializer

    limit = int(request.data.get('limit', 10))
    page = int(request.data.get('page', 1))

    projects = Project.objects.filter(status='1').order_by('-system_creation_time')
    paginator = Paginator(projects, limit)
    page_obj = paginator.get_page(page)

    serialized = ProjectSerializer(page_obj, many=True).data

    return Response({
        "status": "OK",
        "message": "Projects retrieved successfully",
        "data": serialized
    })
@api_view(['POST'])
def delete_project(request):
    project_id = request.data.get('id')

    if not project_id:
        return Response({"status": "error", "message": "Missing 'id'", "data": {}}, status=400)

    if str(project_id).isdigit():
        project = Project.objects.filter(id=project_id, status='1').first()
    else:
        decoded_id = md5_decode_project_id(project_id, Project)
        project = Project.objects.filter(id=decoded_id, status='1').first()

    if not project:
        return Response({"status": "error", "message": "Project not found", "data": {}}, status=404)

    project.status = '5'
    project.save()

    return Response({
        "status": "OK",
        "message": "Project details deleted successfully",
        "data": {}
    })

