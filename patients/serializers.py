from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source = 'user.username')
    password = serializers.CharField(source = 'user.password')
    email = serializers.CharField(source = 'user.email')
    phone_number = serializers.CharField(source = 'user.phone_number')
    class Meta:
        model = Patient
        #fields = '__all__'
        fields = ['user', 'username', 'password', 'email', 'phone_number', 'name', 'area', 'dob']

    def __init__(self, *args, **kwargs):
        # Dynamically set fields based on the 'fields' parameter
        fields = kwargs.pop('fields', None)
        super(PatientSerializer, self).__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

