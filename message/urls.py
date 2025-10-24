"""
URL configuration for emp_dummy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('/', admin.site.urls),
# ]


from django.urls import path
from .views import( create_message, list_project_messages, list_employee_messages)
urlpatterns = [
    # Message APIs
    path('create', create_message, name='create_message'),
    path('messages', list_project_messages, name='list_project_messages'),
    path('employee/messages', list_employee_messages, name='list_employee_messages'),

]