from rest_framework import serializers
from .models import Employee
from django.contrib.auth.hashers import make_password
from .hashid import encode_id
from .md5_hash import md5_hash_id
class UserSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField() #this is to fetch hashed id

    class Meta:
        model = Employee
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'address', 
            'profile_image_url'
            ]  # don't include 'id' if you want to hide it
        extra_kwargs = {
            'system_creation_time': {'required': False},
            'system_update_time': {'required': False},
            
        }

    def get_id(self, obj):
        # return encode_id(obj.id)
        return md5_hash_id(obj.id)

class EmployeeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField() #this is to fetch hashed id
    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs = {
            'system_creation_time': {'required': False},
            'system_update_time': {'required': False},
            'status': {'required': False ,"allow_blank":False},
        }
    def get_id(self, obj):
        # return encode_id(obj.id)
        return md5_hash_id(obj.id)

    def create(self, validated_data):
        if 'status' not in validated_data or not validated_data['status']:
            validated_data['status'] = '1'  # set default
        # Hash the password before saving
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        # Handle default timestamp if not passed
        if 'system_creation_time' not in validated_data:
            from django.utils.timezone import now
            validated_data['system_creation_time'] = now()

        return super().create(validated_data)
    # show all employee details
    def get_emp_details(self,obj):
        return{
            "status":"OK",
            "id":obj.id,
            "first_name":obj.first_name,
            "last_name":obj.last_name,
            "user_name":obj.user_name,
            "email":obj.email,
            "phone_number":obj.phone_number,
            "address":obj.address,
            "profile_image_url":obj.profile_image_url,
            "system_creation_time":obj.system_creation_time,
            "system_update_time":obj.system_update_time,
            "status":obj.status
        }
        
