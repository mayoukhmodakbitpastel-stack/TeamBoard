from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as drf_status
from django.core.paginator import Paginator
from .serializers import ProjectSerializer, ProjectMemberSerializer
from .models import Project,ProjectMember
from .md5_hash import md5_hash_project_id, md5_decode_project_id
from employee.md5_hash import md5_hash_id as md5_hash_employee_id, md5_decode_id as md5_decode_employee_id

# @api_view(['POST'])
# def create_project(request):
#     serializer = ProjectSerializer(data=request.data)
#     if serializer.is_valid():
#         project = serializer.save()
#         response_data = ProjectSerializer(project).data
#         # is admin = True by default for creator
#         return Response({
#             "status": "OK",
#             "message": "Project created successfully",
#             "data": response_data
#         }, status=drf_status.HTTP_201_CREATED)
    
#     return Response({
#         "status": "error",
#         "message": "Validation failed",
#         "data": serializer.errors
#     }, status=drf_status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        project = serializer.save()
        response_data = ProjectSerializer(project).data

        # Create ProjectMember entry with is_admin=True for the creator
        ProjectMember.objects.create(
            project=project,
            member=project.created_by,  # link to creator employee
            is_admin=True,
            status='1'  # assuming active status is '1'
        )

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

    
    # data = ProjectSerializer(project).data
    data = dict(ProjectSerializer(project).data)
    
    # get member hash ids
    data['id'] = md5_hash_project_id(project.id)
    
    # Include members in the project detail
    members = ProjectMember.objects.filter(project=project, status='1')
    data['members'] = [
        {"id": md5_hash_employee_id(m.member.id), "first_name": m.member.first_name, "is_admin": m.is_admin}
        for m in members
    ]

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

# -------- Project Membership APIs -------- #

@api_view(['POST'])
def add_member(request):
    serializer = ProjectMemberSerializer(data=request.data)
    if serializer.is_valid():
        # get validated data to check existence before saving
        project = serializer.validated_data.get('project')
        member_emp = serializer.validated_data.get('member')
        # check if member already exists in project with active status
        existing_member = ProjectMember.objects.filter(project=project, member=member_emp, status='1').first()
        if existing_member:
            return Response({
                "status": "error",
                "message": "Member already exists in project",
                "data": {}
            }, status=400)

        member = serializer.save()
        return Response({
            "status": "OK",
            "message": "Member added successfully",
            "data": ProjectMemberSerializer(member).data
        })
    return Response({
        "status": "error",
        "message": "Validation failed",
        "data": serializer.errors
    }, status=400)


@api_view(['POST'])
def remove_member(request):
    project_id = request.data.get('project_id')
    member_id = request.data.get('member_id')

    if not project_id or not member_id:
        return Response({"status": "error", "message": "Missing IDs", "data": {}}, status=400)

    decoded_proj = md5_decode_project_id(project_id, Project)
    decoded_emp = md5_decode_employee_id(member_id, ProjectMember.member.field.related_model)

    member = ProjectMember.objects.filter(project_id=decoded_proj, member_id=decoded_emp, status='1').first()
    if not member:
        return Response({"status": "error", "message": "Member not found in project", "data": {}}, status=404)

    member.status = '5'
    member.save()

    return Response({
        "status": "OK",
        "message": "Member removed successfully",
        "data": {"project_id": project_id, "member_id": member_id}
    })
    
@api_view(['POST'])
def list_members(request):
    project_id = request.data.get('project_id')
    if not project_id:
        return Response({"status": "error", "message": "Missing 'project_id'", "data": {}}, status=400)

    decoded_proj = md5_decode_project_id(project_id, Project)
    members = ProjectMember.objects.filter(project_id=decoded_proj, status='1')

    limit = int(request.data.get('limit', 10))
    page = int(request.data.get('page', 1))
    paginator = Paginator(members, limit)
    page_obj = paginator.get_page(page)

    data = [
        {
            "id": md5_hash_employee_id(m.member.id),  # hashed member id here
            "first_name": m.member.first_name,
            "is_admin": m.is_admin
        }
        for m in page_obj
    ]

    return Response({
        "status": "OK",
        "message": "Project members retrieved successfully",
        "data": data
    })