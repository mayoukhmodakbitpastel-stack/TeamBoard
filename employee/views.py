from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer, UserSerializer
# from .hashid import decode_id
from .md5_hash import md5_hash_id, md5_hash_id as hash_id, md5_hash_id
from .md5_hash import md5_hash_id

@api_view(['POST'])
def create_employee(request):
    serializer = EmployeeSerializer(data=request.data)
    # mail duplicate check
    email = request.data.get('email')
    if Employee.objects.filter(email=email).exists():
        return Response({"status": "ERROR", "message": "Email already exists.","data":{}}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "Status": "OK",
            "Message": "Employees created successfully.",
            "Data": serializer.data,
        }, status=status.HTTP_201_CREATED)

    # Print the errors to terminal and return them
    print(serializer.errors)
    return Response({"Status": "Error", "Message": "Validation failed","data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])  # POST request for listing employees
def list_employees(request):
    limit = request.data.get('limit')
    page = request.data.get('page')
    employees = Employee.objects.all()
    status_filter = request.data.get('status')
    if status_filter:
        employees = employees.filter(status=status_filter)
        
    # Apply pagination only if both limit and page are valid integers
    try:
        limit = int(limit) if limit is not None else None
        page = int(page) if page is not None else None
    except ValueError:
        return Response({
            "Status": "ERROR",
            "Message": "Limit and page must be integers.",
            "Data": {}
        }, status=status.HTTP_400_BAD_REQUEST)

    if limit is not None and page is not None:
        if limit <= 0 or page <= 0:
            return Response({
                "Status": "ERROR",
                "Message": "Limit and page must be positive integers.",
                "Data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate start and end indices for slicing
        start = (page - 1) * limit
        end = start + limit
        employees = employees[start:end]

    serializer = EmployeeSerializer(employees, many=True)
    return Response({
        "Status": "OK",
        "Message": "Employees retrieved successfully.",
        "Data": serializer.data,
        # "pagination": {
        #     "limit": limit,
        #     "page": page,
        #     "total": Employee.objects.count()
        # }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_employee(request):
    # numeric_id = request.data.get('id')
    hashed_id = request.data.get('id')

    if hashed_id:
        # search by hashed_id
        matched_employee = None
        for emp in Employee.objects.all():
            if md5_hash_id(emp.id) == hashed_id:
                matched_employee = emp
                break
        if not matched_employee:
            return Response({
                "Status": "ERROR",
                "Message": "No employee found with the given id",
                "Data": {}
            }, status=status.HTTP_404_NOT_FOUND)
        employee = matched_employee
    # elif numeric_id:
    #     # Fetch directly by ID
    #     # try:
    #     #     employee = Employee.objects.get(id=numeric_id)
    #     # except Employee.DoesNotExist:
    #     return Response({
    #             "Status": "Error",
    #             "Message": f"Sorry, no employee found with id = {numeric_id}",
    #             "Data": {}
    #         }, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({
            "Status": "ERROR",
            "Message": "Please provide 'id'.",
            "Data": {}
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(employee)
    return Response({
        "Status": "success",
        "Message": "Employee details retrieved successfully"    ,
        "Data": serializer.data
    }, status=status.HTTP_200_OK)
    
# soft delete employee and details and set status to 0
@api_view(['POST'])
def delete_employee(request):
    # emp_id = request.data.get('id')
    hashed_id = request.data.get('id')

    employee = None
    
    if hashed_id:
        # Brute-force search for the employee using hashed ID
        for emp in Employee.objects.all():
            if md5_hash_id(emp.id) == hashed_id:
                employee = emp
                break
        if not employee:
            return Response({
                "status": "ERROR",
                "message": "No employee found with the given hashed_id",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({
            "status": "ERROR",
            "message": "Please provide either 'id' or 'hashed_id'.",
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)

    # Perform soft-delete by setting status = '5'
    employee.status = '5'
    employee.save()

    return Response({
        "status": "OK",
        "message": "Employee details deleted successfully",
        "data": {}
    }, status=status.HTTP_200_OK)
