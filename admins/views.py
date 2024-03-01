from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta, date
from .models import Admin
from .serializers import AdminSerializer, DoctorVerificationSerializer
from users.models import User
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer

class AdminLoginView(generics.GenericAPIView):
    serializer_class = AdminSerializer
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        admin = Admin.objects.filter(user__username = username, user__password = password).first()
        if admin is not None:
            return Response({'responseCode': 200, 'username': username})
        else:
            return Response({'responseCode': 400, 'status': 'Invalid Username or Password'})

class GetUnverifiedDoctors(generics.RetrieveAPIView):
    serializer_class = DoctorSerializer
    def get(self, request):
        doctors = Doctor.objects.filter(verified = False)
        print(doctors)
        serializer = DoctorSerializer(doctors, many = True)
        return Response({'responseCode': 200, 'doctors': serializer.data})
    
class DoctorVerificationView(generics.RetrieveAPIView):
    serializer_class = AdminSerializer
    def post(self, request, *args, **kwargs):
        doctor = request.data.get('doctor')
        admin = request.data.get('admin')
        doctor = Doctor.objects.filter(user__username = doctor).first()
        admin = Admin.objects.filter(user__username = admin).first()
        if doctor is not None and admin is not None:
            serializer = DoctorVerificationSerializer(data = {'doctor': doctor.pk, 'admin': admin.pk}, fields = ['doctor', 'admin'])
            if serializer.is_valid():
                serializer.save()
                doctor.verified = True
                doctor.save()
                return Response({'responseCode': 200, 'status': 'Doctor Verified'})
            else:
                return Response({'responseCode': 400, 'status': serializer.errors})
        else:
            return Response({'responseCode': 400, 'status': 'Doctor or Admin does not exist'})
        
class DoctorDeleteView(generics.RetrieveAPIView):
    def post(self, request, *args, **kwargs):
        doctor = request.data.get('doctor')
        admin = request.data.get('admin')
        doctor = Doctor.objects.filter(user__username = doctor).first()
        admin = Admin.objects.filter(user__username = admin).first()
        if doctor is not None and admin is not None:
            serializer = DoctorVerificationSerializer(data = {'doctor': doctor.pk, 'admin': admin.pk, 'action': 'delete'}, fields = ['doctor', 'admin', 'action'])
            if serializer.is_valid():
                serializer.save()
                doctor.delete()
                return Response({'responseCode': 200, 'status': 'Doctor Deleted'})
            else:
                return Response({'responseCode': 400, 'status': serializer.errors})
        else:
            return Response({'responseCode': 400, 'status': 'Doctor or Admin does not exist'})