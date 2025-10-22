# employee/models.py

from django.db import models
from .md5_hash import md5_hash_id as md5_hash_employee_id
class Employee(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    profile_image_url = models.URLField(null=True, blank=True)
    system_creation_time = models.DateTimeField()
    system_update_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=1,
        choices=[('0', 'Inactive'), ('1', 'Active'), ('5', 'Suspended')],
        default='1',
        )

    class Meta:
        db_table = 'employees' 
        managed = False         
    def get_id(self):
        return md5_hash_employee_id(self.id)

