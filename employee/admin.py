from django.contrib import admin
from .models import Employee
# Register your models here.
admin.site.register(Employee)
admin.site.site_header = "Employee Management Admin"
admin.site.site_title = "Employee Management Admin Portal"
admin.site.index_title = "Welcome to Employee Management Portal"