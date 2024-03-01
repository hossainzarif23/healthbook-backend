from rest_framework import serializers
from .models import Hospital, Doctor, Clinic, Consultency, ConsultencyDay, Degree, Rating

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ('name', 'location')

class ConsultencyDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultencyDay
        #fields = "__all__"
        fields = ('day',)

class ConsultencySerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source = 'clinic.name')
    days = ConsultencyDaySerializer(many = True)
    class Meta:
        model = Consultency
        fields = ('clinic_name', 'room', 'days', 'start_time', 'end_time')

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ('degree', 'speciality')

class DoctorSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source = 'hospital.name', read_only = True)
    username = serializers.CharField(source = 'user.username', read_only = True)
    password = serializers.CharField(source = 'user.password', read_only = True)
    email = serializers.CharField(source = 'user.email', read_only = True)
    phone_number = serializers.CharField(source = 'user.phone_number', read_only = True)
    consultency = ConsultencySerializer(many = True, read_only = True)
    degree = DegreeSerializer(many = True, read_only = True)
    class Meta:
        model = Doctor
        fields = ('user', 'username', 'password', 'name', 'email', 'phone_number', 'area', 'dob', 'description', 'hospital', 'hospital_name', 'department', 'degree', 'designation', 'consultency', 'verified')

    def __init__(self, *args, **kwargs):
        # Dynamically set fields based on the 'fields' parameter
        fields = kwargs.pop('fields', None)
        super(DoctorSerializer, self).__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class AddDegreeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source = 'doctor.user.username')
    class Meta:
        model = Degree
        fields = ('username', 'doctor', 'degree', 'speciality')

class AddConsultencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultency
        fields = '__all__'

class AddConsultencyDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultencyDay
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'