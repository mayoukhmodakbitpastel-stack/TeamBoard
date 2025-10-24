from django.db import models
from employee.models import Employee 
from project.models import Project, ProjectMember

class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_messages')
    text_body = models.TextField()
    has_media = models.BooleanField(default=False)
    media_url = models.URLField(blank=True, null=True)
    system_creation_time = models.DateTimeField(auto_now_add=True)
    system_update_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, default='1')  # 1=active, 0=inactive, 5=deleted

    class Meta:
        db_table = 'messages'

    def __str__(self):
        return f"{self.sender.first_name} - {self.text_body[:30]}"
