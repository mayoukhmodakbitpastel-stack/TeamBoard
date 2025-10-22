from django.db import models
from employee.models import Employee  # assuming this is your user model

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner_image_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='created_projects')
    status = models.CharField(max_length=1, default='1')  # '1' = active, '0' = inactive, '5' = deleted
    system_creation_time = models.DateTimeField(auto_now_add=True)
    system_update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project' 

    def __str__(self):
        return self.title
