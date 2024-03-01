from rest_framework import serializers
from .models import Admin, DoctorVerification

class AdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source = 'user.username')
    password = serializers.CharField(source = 'user.password')
    email = serializers.CharField(source = 'user.email')
    phone_number = serializers.CharField(source = 'user.phone_number')
    class Meta:
        model = Admin
        fields = '__all__'

class DoctorVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorVerification
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Dynamically set fields based on the 'fields' parameter
        fields = kwargs.pop('fields', None)
        super(DoctorVerificationSerializer, self).__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)