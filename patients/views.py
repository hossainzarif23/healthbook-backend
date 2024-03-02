from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from datetime import datetime, timedelta, date
from .models import Patient
from users.models import User
from .serializers import PatientSerializer
from users.serializers import UserSerializer
from doctors.models import Doctor, Hospital, Rating
from doctors.serializers import HospitalSerializer, DoctorSerializer, RatingSerializer
from treatments.models import Request, Prescription, PrescriptionAccess, Medicine, Diagnosis, Treatment, ShareTreatment
from treatments.serializers import TreatmentSerializer, RequestSerializer, PrescriptionSerializer, PrescriptionAccessSerializer, MedicineSerializer, DiagnosisSerializer, ShareTreatmentSerializer

from django.http.response import JsonResponse
from django.utils.dateparse import parse_date

from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
# import matplotlib
# matplotlib.use('SVG')

# Create your views here.

class PatientSignupView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        password_confirmation = request.data.get('password_confirmation', None)
        email = request.data.get('email', None)
        phone_number = request.data.get('phone_number', None)
        name = request.data.get('name', None)
        dob = request.data.get('dob', None)
        
        if password != password_confirmation:
            return Response({'error': "Password doesn't match"})

        if User.objects.filter(username = username).exists():
            return Response({'error': 'Username is already taken', 'responseCode': 400}, status = status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email = email).exists():
            return Response({'error': 'Email is already taken', 'responseCode': 400}, status = status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(phone_number = phone_number).exists():
            return Response({'error': 'Phone Number is already taken', 'responseCode': 400}, status = status.HTTP_400_BAD_REQUEST)
        
        user_serializer = UserSerializer(data = {
            'username': username,
            'password': password,
            'email': email,
            'phone_number': phone_number
        })

        if user_serializer.is_valid():
            user_serializer.save()
            user = User.objects.get(username = username)
            print(user)
            dynamic_attributes = ['user', 'name', 'dob']
            patient_serializer = PatientSerializer(data = {
                'user': user.username,
                'name': name,
                'dob': dob
            }, fields = dynamic_attributes)
            if patient_serializer.is_valid():
                patient_serializer.save()
                return Response({'responseCode': 201, 'status': 'Patient created', 'username': username})
            else:
                user.delete()
                return Response({'responseCode': 400, 'status': patient_serializer.errors})
        else:
            return Response({'responseCode': 400, 'status': user_serializer.errors})
        
class PatientLoginView(generics.RetrieveAPIView):
    serializer_class = PatientSerializer
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        patient = Patient.objects.filter(user__username = username, user__password = password).first()

        if patient is not None:
            return Response({'responseCode': 200, 'username': username})
        else:
            return Response({'responseCode': 400, 'responseText': 'Incorrect username or password'})
        
class PatientProfileView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        requesting_username = request.GET.get('requesting_username', None)

        patient = Patient.objects.filter(user__username = username).first()

        if patient is not None:
            if username == requesting_username:
                dynamic_attributes = ['username', 'password', 'name', 'email', 'phone_number', 'dob', 'area']
                return Response({'responseCode': 200, 'patient': PatientSerializer(patient, fields = dynamic_attributes).data})
            else:
                dynamic_attributes = ['username', 'name', 'email', 'area']
                return Response({'responseCode': 200, 'patient': PatientSerializer(patient, fields = dynamic_attributes).data})
                
        return Response({'responseCode': 400}, status = status.HTTP_400_BAD_REQUEST)
    
class PatientUpdateProfileView(generics.UpdateAPIView):
    serializer_class = PatientSerializer

    def update(self, request, *args, **kwargs):
        username = request.data['username']
        email = request.data['email']
        phone_number = request.data['phone_number']
        password = request.data['password']
        patient = Patient.objects.filter(user__username = username).first()
        other_users = User.objects.exclude(user__username = username)
        if patient is None:
            return Response({"error": "Patient doesn't exist", "responseCode": 400}, status = status.HTTP_400_BAD_REQUEST)
        if other_users.filter(email = email).exists():
            return Response({'error': 'Email is already taken', 'responseCode': 400}, status = status.HTTP_400_BAD_REQUEST)
        if other_users.filter(phone_number = phone_number).exists():
            return Response({'error': 'Phone Number is already taken', 'responseCode': 400}, status = status.HTTP_400_BAD_REQUEST)
        if password != patient.user.password:
            return Response({'error': 'Password Mismatch', 'responseCode': 400}, status = status.HTTP_400_BAD_REQUEST)
        
        patient.user.email = email
        patient.user.phone_number = phone_number
        patient.name = request.data['name']
        patient.area = request.data['area']
        patient.dob = request.data['dob']
        patient.save()

        return Response({'ResponseCode': 200, 'status': 'Patient Updated successfully'})
    
class ListofDoctors(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        department = request.GET.get('department', None)
        designation = request.GET.get('designation', None)
        area = request.GET.get('area', None)
        name = request.GET.get('name', None)

        doctors = Doctor.objects.all()
        if department:
            doctors = doctors.filter(department = department)

        if designation:
            doctors = doctors.filter(designation = designation)

        if area:
            doctors = doctors.filter(consultency__clinic__area = area)

        if name:
            doctors = doctors.filter(name = name)

        dynamic_attributes = ['username', 'name', 'hospital_name', 'department', 'designation', 'consultency']
        return Response({'ResponseCode': 200, 'doctors': DoctorSerializer(doctors, fields = dynamic_attributes, many = True).data})
    
class DoctorProfile(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        doctor = Doctor.objects.filter(user__username = username).first()

        if doctor is not None:
            dynamic_attributes = ['username', 'name', 'email', 'phone_number', 'description', 'hospital_name', 'department', 'degree', 'designation', 'consultency']
            return Response({'ResponseCode': 200, 'doctor': DoctorSerializer(doctor, fields = dynamic_attributes).data})
        return Response({'ResponseCode': 400}, status= status.HTTP_400_BAD_REQUEST)
    
class GetPendingRequests(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        username = request.GET.get('username')
        requests = Request.objects.filter(patient__user__username = username, status = 'pending', date = date.today())

        #print(date.today())

        dynamic_attributes = ['doctor_username']
        return Response({'ResponseCode': 200, 'requests': RequestSerializer(requests, fields = dynamic_attributes, many = True).data})

class RequestUpdateStatusView(generics.UpdateAPIView):
    serializer_class = RequestSerializer

    def update(self, request, *args, **kwargs):
        print(request.data)
        doctor_username = request.data['doctor_username']
        patient_username = request.data['patient_username']
        status = request.data['status']
        request = Request.objects.filter(patient__user__username = patient_username, doctor__user__username = doctor_username, date = date.today()).first()

        if request is None:
            return Response({'responseCode': 400, 'status': 'Request object is not present'})

        if request.status == 'pending':
            request.status = status
            request.save()
            return Response({'responseCode': 200, 'status': 'Request Accepted'})
        return Response({'responseCode': 400, 'status': 'Request was already accepted or rejected'})
    
class UploadPrescriptionView(generics.CreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def create(self, request, *args, **kwargs):
        print('prescription upload requested')
        data = request.data
        print(data)
        # patient = data.get('patient', None)
        # patient_object = Patient.objects.filter(user__username = patient).first()
        # if patient_object is None:
        #     return Response({'responseCode': 404, 'status': 'no valid patient'})
        # data['patient_name'] = patient_object.name
        # data['patient_username'] = patient_object.user.username
        # data['patient'] = patient_object.pk
        dynamic_attributes = ['age', 'weight', 'height', 'address', 'bp_low', 'bp_high', 'treatment', 'notes', 'next_appointment', 'symptoms', 'tests', 'diagnoses', 'advices', 'medicines', 'date']
        serializer = PrescriptionSerializer(data = data, fields = dynamic_attributes)
        if serializer.is_valid():
            prescription = serializer.save()
            response_serializer = self.get_serializer(prescription)
            return Response(response_serializer.data, status = 201)
        else:
            return Response(serializer.errors, status = 400)
        
class GetPrescriptionView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        id = request.GET.get('id', None)
        username = request.GET.get('username', None);
        prescription = Prescription.objects.filter(pk = id).first()
        if prescription is None:
            return Response({'responseCode': '404', 'status': 'Prescription not found'})
        if username != prescription.treatment.patient.user.username:
            return Response({'responseCode': '400', 'status': 'Access not allowed'})
        return Response({'responseCode': '200', 'prescription': PrescriptionSerializer(prescription).data})
    
class GetPrescriptionAccessView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient_username = request.GET.get('patient_username')
        queryset = PrescriptionAccess.objects.filter(patient__user__username=patient_username)
        serializer = PrescriptionAccessSerializer(queryset, many = True)
        return Response(serializer.data)
    
class PrescriptionAccessUpdateAPIView(generics.UpdateAPIView):
    def patch(self, request, *args, **kwargs):
        patient_username = request.data.get('patient_username', None)
        doctor_username = request.data.get('doctor_username', None)
        prescription_id = request.data.get('prescription_id', None)
        status = request.data.get('status', None)
        prescription_access = PrescriptionAccess.objects.get(patient__user__username = patient_username, doctor__user__username = doctor_username, prescription__id = prescription_id)
        if prescription_access.status != 'pending':
            return Response({'responseCode': '400', 'status': 'Wrong request'})
        if status != 'accepted' and status != 'rejected':
            print(status)
            return Response({'responseCode': '400', 'status': 'Wrong request status'})
        if prescription_access is None:
            return Response({'responseCode': '404', 'status': 'Update not allowed'})
        serializer = PrescriptionAccessSerializer(prescription_access, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'request': serializer.data})
        return Response({'responseCode': 404, 'status': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class GetListofprescriptionView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        user = request.GET.get('user', None)
        patient = request.GET.get('patient', None)
        days = request.GET.get('month', None)
        treatment = request.GET.get('treatment', None)
        if user != patient:
            return Response({'responseCode': 400, 'status': 'Not authorized to view prescription'})
        prescriptions = Prescription.objects.filter(treatment__patient__user__username = patient).all()
        if treatment is not None:
            prescriptions = prescriptions.filter(treatment = treatment)
        # if days is not None:
        #     days = days * 30
        #     current_date = datetime.now().date()
        #     min_valid_date = current_date - timedelta(days=Medicine.objects.first().duration)
        #     prescriptions = prescriptions.filter(date__gte = min_valid_date)
        if len(prescriptions) > 0:
            return Response({'responseCode': 200, 'prescriptions': PrescriptionSerializer(prescriptions, many = True).data})
        else:
            return Response({'responseCode': 404, 'status': 'No prescription found'})
        
class GetCurrentMedicinesView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        user = request.GET.get('user', None)
        patient = request.GET.get('patient', None)
        disease = request.GET.get('disease', None)
        current_date = datetime.now().date()
        min_valid_date = current_date - timedelta(days=Medicine.objects.first().duration)

        if user != patient:
            return Response({'responseCode': 400, 'status': 'Not authorized to view prescription'})
        medicines = Medicine.objects.filter(prescription__treatment__patient__user__username = patient, prescription__date__gte = min_valid_date).all()
        print(medicines)
        if len(medicines) > 0:
            return Response({'responseCode': 200, 'medicines': MedicineSerializer(medicines, many = True).data})
        else:
            return Response({'responseCode': 404, 'status': 'No medicine found'})
        
class GetCurrentDiseaseView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        user = request.GET.get('user', None)
        patient = request.GET.get('patient', None)
        #disease = request.GET.get('disease', None)
        current_date = datetime.now().date()
        min_valid_date = current_date - timedelta(days=Medicine.objects.first().duration)
        if user != patient:
            return Response({'responseCode': 400, 'status': 'Not authorized to view prescription'})
        #diagnoses = Diagnosis.objects.filter(prescription__patient__username = patient, prescription__date__gte = min_valid_date, disease__icontains = disease).all()
        diagnoses = Diagnosis.objects.filter(prescription__patient__user__username = patient, prescription__date__gte = min_valid_date).all()
        if len(diagnoses) > 0:
            return Response({'responseCode': 200, 'medicines': DiagnosisSerializer(diagnoses, many = True).data})
        else:
            return Response({'responseCode': 404, 'status': 'No disease found'})
        
class CreateTreatmentView(generics.CreateAPIView):
    def post(self, request):
        patient_username = request.data.get('patient_username', None)
        # doctor_username = request.data.get('doctor_username')
        disease = request.data.get('disease', None)
        verified = 'no'
        doctor_name = request.data.get('doctor_name', None)
        speciality = request.data.get('speciality', None)
        designation = request.data.get('designation', None)
        hospital = request.data.get('hospital_name', None)
        start_date = request.data.get('start_date', None)
        last_date = request.data.get('last_date', None)
        status = request.data.get('status', None)
        cost = request.data.get('cost', 0)

        if start_date is None or start_date == '':
            start_date = date.today()

        if last_date is None or last_date == '':
            last_date = date.today()

        print(patient_username)
        print(disease)
        print(verified)
        print(doctor_name)
        print(speciality)
        print(designation)
        print(hospital)
        print("start_date is ", start_date)
        print("last date is ", last_date)
        print(status)
        print(cost)

        # Retrieve patient and doctor objects
        try:
            patient = Patient.objects.get(user__username = patient_username)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=404)
        # try:
        #     doctor = Doctor.objects.get(user__username=doctor_username)
        # except Doctor.DoesNotExist:
        #     return Response({'error': 'Doctor not found'}, status=404)

        # Create the treatment object
        serializer = TreatmentSerializer(data={
            'patient': patient.pk,  # Use primary key for relationships
            'disease': disease,
            'verified': verified,
            'doctor_name': doctor_name,
            'speciality': speciality,
            'designation': designation,
            'hospital_name': hospital,
            'status': status,
            'start_date': start_date,
            'last_date': last_date,
            'cost': cost,
        }, fields = ['patient', 'disease', 'verified', 'doctor_name', 'speciality', 'designation', 'hospital_name', 'status', 'start_date', 'last_date', 'cost'])

        if serializer.is_valid():
            serializer.save()
            # return Response(serializer.data, status=201)
            print(patient.pk)
            print(disease)
            print(start_date)
            print(last_date)
            print(verified)
            print(doctor_name)
            print(speciality)
            print(designation)
            print(hospital)
            print(status)
            treatment = TreatmentSerializer(Treatment.objects.filter(patient = patient.pk, disease = disease, start_date = start_date, last_date = last_date, verified = verified, doctor_name = doctor_name, speciality = speciality, designation = designation, hospital_name = hospital, status = status).first(), fields = ['id', 'patient', 'status', 'start_date', 'last_date', 'disease', 'verified', 'doctor_name', 'speciality', 'designation', 'hospital_name']).data
            return Response({'responseCode': 200, 'status': 'Treatment created', 'treatment': treatment})
        else:
            #return Response(serializer.errors, status=400)
            return Response({'responseCode': 400, 'status': serializer.errors})

class UpdateTreatmentView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        patient_username = request.data.get('patient_username', None)
        # doctor_username = request.data.get('doctor_username')
        disease = request.data.get('disease', None)
        verified = 'no'
        doctor_name = request.data.get('doctor_name', None)
        speciality = request.data.get('speciality', None)
        designation = request.data.get('designation', None)
        hospital = request.data.get('hospital_name', None)
        start_date = request.data.get('start_date', None)
        last_date = request.data.get('last_date', None)
        status = request.data.get('status', None)
        cost = request.data.get('cost', 0)
        treatment = request.data.get('treatment', None)
        treatment = Treatment.objects.filter(pk = treatment, patient__user__username = patient_username).first()
        if treatment is None:
            return Response({'responseCode': 404, 'status': 'Treatment not found'})
        
        # Retrieve patient and doctor objects
        try:
            patient = Patient.objects.get(user__username = patient_username)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=404)
        
        serializer = TreatmentSerializer(treatment, data = {
            'patient': patient.pk,  # Use primary key for relationships
            'disease': disease,
            'verified': verified,
            'doctor_name': doctor_name,
            'speciality': speciality,
            'designation': designation,
            'hospital_name': hospital,
            'status': status,
            'start_date': start_date,
            'last_date': last_date,
            'cost': cost,
        }, fields = ['patient', 'disease', 'verified', 'doctor_name', 'speciality', 'designation', 'hospital_name', 'status', 'start_date', 'last_date', 'cost'])
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Treatment updated'})
        else:
            return Response({'responseCode': 400, 'status': serializer.errors})

        
class GetTreatmentView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        treatment = request.GET.get('treatment', None)
        treatment_obj = Treatment.objects.filter(patient__user__username = patient, id = treatment).first()
        if treatment_obj is None:
            return Response({'responseCode': 404, 'status': 'No treatment found'})
        return Response({'responseCode': 200, 'treatment': TreatmentSerializer(treatment_obj).data})

class GetTreatmentsView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        user = request.GET.get('user', None)
        patient = request.GET.get('patient', None)
        if user != patient:
            return Response({'responseCode': 400, 'error': 'Not allowed to view others treatment'})
        # treatments = Treatment.objects.filter(patient__user__username = patient, status = 'ongoing').all()
        treatments = Treatment.objects.filter(patient__user__username = patient).all()
        return Response({'responseCode': 200, 'treatment': TreatmentSerializer(treatments, many = True).data})
        
class GetCurrentTreatmentsView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        user = request.GET.get('user', None)
        patient = request.GET.get('patient', None)
        if user != patient:
            return Response({'responseCode': 400, 'error': 'Not allowed to view others treatment'})
        treatments = Treatment.objects.filter(patient__user__username = patient, status = 'ongoing').all()
        # treatments = Treatment.objects.filter(patient__user__username = patient).all()
        return Response({'responseCode': 200, 'treatment': TreatmentSerializer(treatments, many = True).data})
    
class ShareTreatmentView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        doctor_username = request.GET.get('doctor', None)
        treatment = request.GET.get('treatment', None)
        treatment_obj = Treatment.objects.filter(pk = treatment).first()
        if patient != treatment_obj.patient.user.username:
            return Response({'responseCode': 400, 'error': 'Not allowed to share others treatment'})
        doctor = Doctor.objects.filter(user__username = doctor_username).first()
        serializer = ShareTreatmentSerializer(data = {
            'doctor_username': doctor_username,
            'treatment': treatment,
            'doctor': doctor.pk
        })
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Treatment shared', 'treatment': serializer.data})
        else:
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class GetSharedTreatmentsView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.data.get('patient', None)
        treatment = request.GET.get('treatment', None)
        treatment_obj = Treatment.objects.filter(pk = treatment).first()
        if treatment_obj.patient.user.username != patient:
            return Response({'responseCode': 400, 'status': 'Not allowed to view others shared treatments'})
        return Response({'responseCode': 200, 'shares': ShareTreatmentSerializer(ShareTreatment.objects.filter(treatment = treatment).all(), many = True).data})
    
class UnShareTreatmentsView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        patient = request.data.get('patient', None)
        doctor = request.data.get('doctor', None)
        treatment = request.data.get('treatment', None)
        treatment_obj = Treatment.objects.filter(pk = treatment).first()
        print(treatment_obj)
        if treatment_obj.patient.user.username != patient:
            return Response({'responseCode': 400, 'status': 'Not allowed to view others shared treatments'})
        shared_obj = ShareTreatment.objects.filter(treatment = treatment, doctor__user__username = doctor).first()
        if shared_obj is None:
            return Response({'responseCode': 200, 'status': "shared treatment doesn't exist"})
        shared_obj.delete()
        return Response({'responseCode': 200, 'status': 'Treatment unshared with doctor'})
    
class AddRatingView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        patient_username = request.data.get('patient', None)
        doctor_username = request.data.get('doctor', None)
        rating = request.data.get('rating', None)

        print("Patient Username:", patient_username)
        patient_instance = Patient.objects.filter(user__username=patient_username).first()
        print("Patient Instance:", patient_instance)

        if patient_instance is None:
            return Response({'responseCode': 400, 'status': 'Patient not found'})

        print("Doctor Username:", doctor_username)
        doctor_instance = Doctor.objects.filter(user__username=doctor_username).first()
        print("Doctor Instance:", doctor_instance)

        if doctor_instance is None:
            return Response({'responseCode': 400, 'status': 'Doctor not found'})

        serializer = RatingSerializer(data={
            'patient': patient_instance.pk,
            'doctor': doctor_instance.pk,
            'rating': rating
        })

        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Rating added'})

        print(serializer.errors)
        
        return Response({'responseCode': 400, 'status': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateRatingView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        patient_username = request.data.get('patient', None)
        doctor_username = request.data.get('doctor', None)
        rating = request.data.get('rating', None)
        print(rating)
        patient_instance = Patient.objects.filter(user__username=patient_username).first()
        if patient_instance is None:
            return Response({'responseCode': 400, 'status': 'Patient not found'})
        doctor_instance = Doctor.objects.filter(user__username=doctor_username).first()
        if doctor_instance is None:
            return Response({'responseCode': 400, 'status': 'Doctor not found'})
        rating_instance = Rating.objects.filter(patient=patient_instance, doctor=doctor_instance).first()
        if rating_instance is None:
            return Response({'responseCode': 400, 'status': 'Rating not found'})
        serializer = RatingSerializer(rating_instance, data={
            'patient': patient_instance.pk,
            'doctor': doctor_instance.pk,
            'rating': rating
        })
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Rating updated'})
        return Response({'responseCode': 400, 'status': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteRatingView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        patient_username = request.data.get('patient', None)
        doctor_username = request.data.get('doctor', None)
        patient_instance = Patient.objects.filter(user__username=patient_username).first()
        if patient_instance is None:
            return Response({'responseCode': 400, 'status': 'Patient not found'})
        doctor_instance = Doctor.objects.filter(user__username=doctor_username).first()
        if doctor_instance is None:
            return Response({'responseCode': 400, 'status': 'Doctor not found'})
        rating_instance = Rating.objects.filter(patient=patient_instance, doctor=doctor_instance).first()
        if rating_instance is None:
            return Response({'responseCode': 400, 'status': 'Rating not found'})
        rating_instance.delete()
        return Response({'responseCode': 200, 'status': 'Rating deleted'})
    
class GetRatingView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient_username = request.GET.get('patient', None)
        doctor_username = request.GET.get('doctor', None)
        patient_instance = Patient.objects.filter(user__username=patient_username).first()
        if patient_instance is None:
            return Response({'responseCode': 400, 'status': 'Patient not found'})
        doctor_instance = Doctor.objects.filter(user__username=doctor_username).first()
        if doctor_instance is None:
            return Response({'responseCode': 400, 'status': 'Doctor not found'})
        rating_instance = Rating.objects.filter(patient=patient_instance, doctor=doctor_instance).first()
        if rating_instance is None:
            return Response({'responseCode': 400, 'status': 'Rating not found'})
        return Response({'responseCode': 200, 'rating': RatingSerializer(rating_instance).data})

class PatientDiseaseFrequencyView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        one_year_ago = date.today() - timedelta(days=365)
        patient_treatments = Treatment.objects.filter(patient__user__username=patient, last_date__gte=one_year_ago).annotate(count=Count('disease'))

        if patient_treatments is None:
            df = pd.DataFrame(columns=['disease', 'count'])
        else:
            columns = ['disease', 'count']
            data = patient_treatments.values_list(*columns)
            df = pd.DataFrame(data, columns=columns)
        
        # print(df)
        plt.figure(figsize=(8, 6))
        plt.bar(df['disease'], df['count'], color='skyblue')
        plt.xlabel('Disease')
        plt.ylabel('Frequency')
        plt.title("Patient's Disease Frequencies (Last Year)")
        
        plt.savefig('disease_treatment_counts.png')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Encode the image data as base64
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Close the buffer to clear resources
        buffer.close()

        response_data = {
            'labels': df['disease'].tolist(),
            'values': df['count'].tolist(),
            'image': f'data:image/png;base64,{image_data}',
        }
        return Response({'responseCode': 200, 'response': response_data})

class PatientTreatmentSuccessRateView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        one_year_ago = date.today() - timedelta(days=365)
        patient_treatments = Treatment.objects.filter(patient__user__username=patient, last_date__gte=one_year_ago).annotate(success_count=Count('id', filter=Q(status='success')), failure_count=Count('id', filter=Q(status='failure')), ongoing_count=Count('id', filter=Q(status='ongoing')))

        if patient_treatments is None:
            df = pd.DataFrame(columns=['disease', 'success_count', 'failure_count', 'ongoing_count'])
        else:
            columns = columns = ['disease', 'success_count', 'failure_count', 'ongoing_count']
            data = patient_treatments.values_list(*columns)
            df = pd.DataFrame(data, columns=columns)
        # Plot side by side bars for success and failure count
        fig, ax = plt.subplots(figsize=(10, 6))
        # Bar width
        bar_width = 0.2
        # Position of bars on x-axis
        r1 = df.index
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]
        # Plot bars for success count
        ax.bar(r1, df['success_count'], width=bar_width, edgecolor='grey', label='Success', color='g')
        # Plot bars for failure count
        ax.bar(r2, df['failure_count'], width=bar_width, edgecolor='grey', label='Failure', color='r')
        # Plot bars for ongoing count
        ax.bar(r3, df['ongoing_count'], width=bar_width, edgecolor='grey', label='Ongoing', color='b')
        # Add labels, title, and legend
        ax.set_xlabel('Disease', fontweight='bold')
        ax.set_ylabel('Count', fontweight='bold')
        ax.set_xticks([r + bar_width for r in range(len(df.index))])
        ax.set_xticklabels(df['disease'])
        ax.set_title('Success, Failure and Ongoing Count for Each Disease')
        ax.legend()
        plt.savefig('disease_treatment_counts.png')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Encode the image data as base64
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Close the buffer to clear resources
        buffer.close()
        
        response_data = {
            # 'labels': df['disease'].tolist(),
            # 'values': df['count'].tolist(),
            'image': f'data:image/png;base64,{image_data}',
        }
        return Response({'responseCode': 200, 'response': response_data})

class PatientDoctorVisitView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        one_year_ago = date.today() - timedelta(days=365)
        prescription_counts = Prescription.objects.filter(treatment__patient__user__username=patient, date__gte=one_year_ago).annotate(month=ExtractMonth('date')).values('month').annotate(count=Count('id'))
        
        # Convert to DataFrame
        if not prescription_counts:
            # If prescription_counts is empty, initialize DataFrame with 0 rows
            df = pd.DataFrame(columns=['month', 'count'])
        else:
            df = pd.DataFrame(prescription_counts)

        all_months_df = pd.DataFrame({'month': range(1, 13)})
        df = pd.merge(all_months_df, df, how='left', on='month').fillna(0)
        df['count'] = df['count'].astype(dtype = 'int')

        # print(df)

        # Plot bar plot
        plt.figure(figsize=(10, 6))
        plt.bar(df['month'], df['count'], color='skyblue')
        plt.xlabel('Month')
        plt.ylabel('Number of Visits to Doctor')
        plt.title('Month-wise Count of Visits to Doctor (Last Year)')
        plt.xticks(range(1, 13))  # Assuming month ranges from 1 to 12
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        plt.savefig('disease_treatment_counts.png')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Encode the image data as base64
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        response_data = {
            # 'labels': df['disease'].tolist(),
            # 'values': df['count'].tolist(),
            'image': f'data:image/png;base64,{image_data}',
        }
        return Response({'responseCode': 200, 'response': response_data})

class RecurringDiseasesView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        three_year_ago = date.today() - timedelta(days = 3 * 365 + 100)
        start_month = (date.today() - timedelta(days = 30)).month
        end_month = (date.today() + timedelta(days = 30)).month
        diseases = Treatment.objects.filter(
            Q(patient__user__username=patient) &
            Q(last_date__gte=three_year_ago) &
            Q(start_date__month__range=[start_month, end_month]) |
            Q(last_date__month__range=[start_month, end_month])
        ).values('disease').annotate(disease_count=Count('disease')).filter(
            disease_count__gte=2,
        )
        response_data = [{'disease': disease['disease'], 'count': disease['disease_count']} for disease in diseases]
        return Response({'responseCode': 200, 'diseases': response_data})
    
class PatientHealthSatisfactionView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        one_year_ago = date.today() - timedelta(days=365)

        treatment_count = Treatment.objects.filter(patient__user__username=patient, last_date__gte=one_year_ago).count()
        prescription_count = Prescription.objects.filter(treatment__patient__user__username=patient, date__gte=one_year_ago).count()
        health_satisfaction = 10 - 0.2 * treatment_count - 0.04 * prescription_count

        return Response({'responseCode': 200, 'health_satisfaction': round(health_satisfaction, 2)})
        