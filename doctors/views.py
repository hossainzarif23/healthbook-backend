from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Hospital, Doctor, Clinic, Consultency, ConsultencyDay, Degree, Rating
from users.models import User
from treatments.models import Request, Prescription, Treatment, PrescriptionAccess, Medicine, Diagnosis
from patients.models import Patient
from patients.serializers import PatientSerializer
from treatments.serializers import RequestSerializer, TreatmentSerializer, PrescriptionSerializer, PrescriptionAccessSerializer, MedicineSerializer, DiagnosisSerializer
from .serializers import HospitalSerializer, DoctorSerializer, DegreeSerializer, AddDegreeSerializer, AddConsultencySerializer, AddConsultencyDaysSerializer, ConsultencySerializer
from users.serializers import UserSerializer
from datetime import datetime, timedelta
from datetime import date
from django.db.models import Count, Q
from django.db.models import Avg
from django.db.models.functions import ExtractMonth

import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Create your views here.

class DoctorSignupView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        password_confirmation = request.data.get('password_confirmation', None)
        email = request.data.get('email', None)
        phone_number = request.data.get('phone_number', None)
        name = request.data.get('name', None)
        dob = request.data.get('dob', None)
        designation = request.data.get('designation', None)
        hospital_name = request.data.get('hospital_name', None)
        department = request.data.get('department', None)

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
            hospital = Hospital.objects.filter(name = hospital_name).first()
            if hospital is None:
                return Response({'error': "Hospital doesn't exist", 'responseCode': 404})
            dynamic_attributes = ['user', 'name', 'dob', 'designation', 'hospital', 'department']
            doctor_serializer = DoctorSerializer(data = {
                'user': user.username,
                'name': name,
                'dob': dob,
                'designation': designation,
                'hospital': hospital.pk,
                'department': department
            }, fields = dynamic_attributes)
            if doctor_serializer.is_valid():
                doctor_serializer.save()
                return Response({'responseCode': 201, 'status': 'Doctor created', 'username': username})
            else:
                user.delete()
                return Response({'responseCode': 400, 'status': doctor_serializer.errors})
        else:
            return Response({'responseCode': 400, 'status': user_serializer.errors})
        
class DoctorLoginView(generics.GenericAPIView):
    serializer_class = DoctorSerializer
    
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        doctor = Doctor.objects.filter(user__username = username, user__password = password).first()

        if doctor is not None:
            return Response({'responseCode': 200, 'username': username})
        else:
            return Response({'responseCode': 400, 'responseText': 'Incorrect username or password'})
        
class DoctorProfileView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        requesting_username = request.GET.get('requesting_username', None)
        doctor = Doctor.objects.filter(user__username = username).first()

        if doctor is not None:
            if username == requesting_username:
                dynamic_attributes = ['username', 'password', 'name', 'email', 'phone_number', 'area', 'dob', 'description', 'hospital_name', 'department', 'degree', 'designation', 'consultency']
                return Response({'ResponseCode': 200, 'doctor': DoctorSerializer(doctor, fields = dynamic_attributes).data})
            else:
                dynamic_attributes = ['username', 'name', 'email', 'phone_number', 'description', 'hospital_name', 'department', 'degree', 'designation', 'consultency']
                return Response({'ResponseCode': 200, 'doctor': DoctorSerializer(doctor, fields = dynamic_attributes).data})

        return Response({'ResponseCode': 400}, status= status.HTTP_400_BAD_REQUEST)
    
class AddDegreeView(generics.CreateAPIView):
    serializer_class = AddDegreeSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        degree = request.data.get('degree', None)
        speciality = request.data.get('speciality', None)

        try:
            doctor = Doctor.objects.get(user__username = username)
        except Doctor.DoesNotExist:
            return Response({'responseCode': 404, 'error': 'Doctor not found'}, status=404)
        
        deg = Degree.objects.filter(doctor = doctor, degree = degree, speciality = speciality).first()
        if deg is not None:
            return Response({'responseCode': 404, 'error': 'Degree already exists'}, status = 404)
        
        request.data['doctor'] = doctor.pk
        
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            # return Response(serializer.data, status=201)
            return Response({'responseCode': 200, 'status': 'Degree added', 'degree': serializer.data})
        else:
            #return Response(serializer.errors, status=400)
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class ListofDegreesView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        degrees = Degree.objects.filter(doctor__user__username = username)
        return Response({'responseCode': 200, 'degrees': DegreeSerializer(degrees, many = True).data})
    
class AddConsultencyView(generics.CreateAPIView):
    serializer_class = AddConsultencySerializer
    def create(self, request, *args, **kwargs):
        doctor_username = request.data.get('doctor_username', None)
        clinic_name = request.data.get('clinic_name', None)
        room = request.data.get('room', None)
        start_time = request.data.get('start_time', None)
        end_time = request.data.get('end_time', None)
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()
        days = request.data.get('days', None)

        # Retrieve patient and doctor objects
        try:
            doctor = Doctor.objects.get(user__username = doctor_username)
            #clinic = Clinic.objects.get(name = clinic_name)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=404)
        
        try:
            clinic = Clinic.objects.get(name=clinic_name)
        except Clinic.DoesNotExist:
            return Response({'error': 'Clinic not found'}, status=404)
        
        serializer = AddConsultencySerializer(data = {
            'room': room,
            'start_time': start_time,
            'end_time': end_time,
            'clinic': clinic.pk,
            'doctor': doctor.pk
        })

        if serializer.is_valid():
            serializer.save()
            consultency = Consultency.objects.get(room = room, start_time = start_time, end_time = end_time, clinic = clinic, doctor = doctor)
            data = []
            for day in days:
                data.append({'consultency': consultency.pk, 'day': day})
            serializer2 = AddConsultencyDaysSerializer(data = data, many = True)
            if serializer2.is_valid():
                serializer2.save()
                return Response({'responseCode': 200, 'status': 'Consultency created', 'consultency': ConsultencySerializer(consultency).data})
            else:
                consultency.delete()
                return Response({'responseCode': 400, 'status': serializer2.errors})
        else:
            #return Response(serializer.errors, status=400)
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class RequestPatientData(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        patient_username = request.data.get('patient_username')
        doctor_username = request.data.get('doctor_username')
        patient = Patient.objects.filter(user__username = patient_username).first()
        doctor = Doctor.objects.filter(user__username = doctor_username).first()
        if patient is None or doctor is None:
            return Response({'responseCode': 404, 'status': 'Patient or Doctor not found'})
        dynamic_attributes = ['patient', 'doctor']
        serializer = RequestSerializer(data = {
            'patient': patient.pk,
            'doctor': doctor.pk
        }, fields = dynamic_attributes)

        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 201, 'id': serializer.instance.id})
        else:
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class CreateTreatmentView(generics.CreateAPIView):
    def post(self, request):
        patient_username = request.data.get('patient_username', None)
        doctor_username = request.data.get('doctor_username', None)
        disease = request.data.get('disease', None)
        hospital = request.data.get('hospital_name', None)
        start_date = date.today()
        last_date = date.today()
        verified = 'yes'

        # Retrieve patient and doctor objects
        try:
            patient = Patient.objects.get(user__username = patient_username)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=404)
        try:
            doctor = Doctor.objects.get(user__username=doctor_username)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=404)

        # Create the treatment object
        serializer = TreatmentSerializer(data={
            'patient': patient.pk,  # Use primary key for relationships
            'doctor': doctor.pk,
            'doctor_name': doctor.name,
            'speciality': doctor.department,
            'designation': doctor.designation,
            'hospital_name': hospital,
            'disease': disease,
            'verified': verified,
            'start_date': start_date,
            'last_date': last_date
        }, fields = ['patient', 'doctor', 'disease', 'verified', 'doctor_name', 'speciality', 'designation', 'hospital_name', 'start_date', 'last_date'])

        if serializer.is_valid():
            serializer.save()
            # return Response(serializer.data, status=201)
            treatment = TreatmentSerializer(Treatment.objects.filter(patient = patient.pk, doctor = doctor.pk, disease = disease, start_date = datetime.now().date(), last_date = datetime.now().date(), verified = verified).first()).data
            return Response({'responseCode': 200, 'status': 'Treatment created', 'treatment': treatment})
        else:
            #return Response(serializer.errors, status=400)
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class UpdateTreatmentView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        patient_username = request.data.get('patient_username', None)
        doctor_username = request.data.get('doctor_username', None)
        treatment = request.data.get('treatment', None)
        status = request.data.get('status', None)
        disease = request.data.get('disease', None)
        cost = request.data.get('cost', None)
        last_date = date.today()
        treatment = Treatment.objects.filter(pk = treatment, doctor__user__username = doctor_username, patient__user__username = patient_username).first()
        if treatment is None:
            return Response({'responseCode': 404, 'status': 'Treatment not found'})
        serializer = TreatmentSerializer(treatment, data = {
            'status': status,
            'disease': disease,
            'last_date': last_date,
            'cost': cost,
        }, fields = ['status', 'disease', 'last_date', 'cost'])
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Treatment updated'})
        else:
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class UploadPrescriptionView(generics.CreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def create(self, request, *args, **kwargs):
        print('prescription upload requested')
        data = request.data
        treatment_id = data.get('treatment')
        treatment = Treatment.objects.get(pk=treatment_id)
        data['date'] = date.today()
        dynamic_attributes = ['age', 'weight', 'height', 'address', 'bp_low', 'bp_high', 'treatment', 'notes', 'next_appointment', 'symptoms', 'tests', 'diagnoses', 'advices', 'medicines', 'date']
        serializer = PrescriptionSerializer(data = data, fields = dynamic_attributes)
        if serializer.is_valid():
            prescription = serializer.save()
            treatment.last_date = date.today()
            response_serializer = self.get_serializer(prescription)
            return Response(response_serializer.data, status = 201)
        else:
            return Response(serializer.errors, status = 400)
        
# class UpdatePrescriptionView(generics.UpdateAPIView):
#     def update(self, request, *args, **kwargs):
#         data = request.data

        
class PrescriptionAccessCreateView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        patient = data.get('patient', None)
        doctor = data.get('doctor', None)
        data['patient_username'] = patient
        data['doctor_username'] = doctor
        patient = Patient.objects.filter(user__username = patient).first()
        doctor = Doctor.objects.filter(user__username = doctor).first()
        if patient is None or doctor is None:
            return Response({'responseCode': 400, 'status': "Patient or Doctor doesn't exist"})
        data['patient'] = patient.pk
        data['doctor'] = doctor.pk

        serializer = PrescriptionAccessSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class GetPrescriptionView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        id = request.GET.get('id', None)
        doctor = request.GET.get('doctor', None)
        prescription = Prescription.objects.filter(pk = id).first()
        print(prescription)
        if prescription is None:
            return Response({'responseCode': 404, 'status': 'prescription not found'})
        return Response({'responseCode': 200, 'prescription': PrescriptionSerializer(prescription).data})
    
class GetListofprescriptionView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        doctor = request.GET.get('doctor', None)
        days = request.GET.get('days', None)
        treatment = request.GET.get('treatment', None)
        print(doctor)
        print(treatment)
        prescriptions = Prescription.objects.filter(treatment = treatment).all()
        if len(prescriptions) > 0:
            return Response({'responseCode': 200, 'prescriptions': PrescriptionSerializer(prescriptions, many = True).data})
        else:
            return Response({'responseCode': 404, 'status': 'No prescription found'})
    
class PatientSearchAPI(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        username = request.GET.get('username')
        patient = Patient.objects.filter(user__username__icontains = username).all()
        if patient is None:
            return Response({'responseCode': 404, 'status' :'Patient not found'})
        dynamic_attributes = ['username', 'password', 'name', 'email', 'area']
        return Response({'responseCode': 200, 'patients': PatientSerializer(patient, fields = dynamic_attributes, many = True).data})
    
class GetCurrentMedicinesView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        doctor = request.GET.get('doctor', None)
        patient = request.GET.get('patient', None)
        disease = request.GET.get('disease', None)
        # access = Request.objects.filter(doctor__user__username = doctor, patient__user__username = patient).first()
        # if access is None or access.status != 'accepted':
        #     return Response({'responseCode': 400, 'status': 'Not authorized to view medicines'})
        current_date = datetime.now().date()
        min_valid_date = current_date - timedelta(days=Medicine.objects.first().duration)
        medicines = Medicine.objects.filter(prescription__treatment__patient__user__username = patient, prescription__date__gte = min_valid_date).all()
        if len(medicines) > 0:
            return Response({'responseCode': 200, 'medicines': MedicineSerializer(medicines, many = True).data})
        else:
            return Response({'responseCode': 404, 'status': 'No medicine found'})
        
class GetCurrentDiseaseView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        doctor = request.GET.get('doctor', None)
        patient = request.GET.get('patient', None)
        #disease = request.GET.get('disease', None)
        current_date = datetime.now().date()
        min_valid_date = current_date - timedelta(days=Medicine.objects.first().duration)
        # access = Request.objects.filter(doctor__user__username = doctor, patient__user__username = patient).first()
        # if access is None or access.status != 'accepted':
        #     return Response({'responseCode': 400, 'status': 'Not authorized to view diseases'})
        #diagnoses = Diagnosis.objects.filter(prescription__patient__username = patient, prescription__date__gte = min_valid_date, disease__icontains = disease).all()
        diagnoses = Diagnosis.objects.filter(prescription__treatment__patient__user__username = patient, prescription__date__gte = min_valid_date).all()
        if len(diagnoses) > 0:
            return Response({'responseCode': 200, 'medicines': DiagnosisSerializer(diagnoses, many = True).data})
        else:
            return Response({'responseCode': 404, 'status': 'No disease found'})
        
class DoctorProfileUpdateView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        doctor = Doctor.objects.filter(user__username = username, user__password = password).first()
        if doctor is None:
            return Response({'responseCode': 404, 'status': 'Doctor not found'})
        other_users = User.objects.exclude(username = username).all()
        if other_users.filter(email = request.data.get('email')).exists():
            return Response({'responseCode': 400, 'status': 'Email already exists'})
        if other_users.filter(phone_number = request.data.get('phone_number')).exists():
            return Response({'responseCode': 400, 'status': 'Phone number already exists'})
        dynamic_attributes = ['username', 'password', 'name', 'email', 'phone_number', 'area', 'dob', 'description', 'hospital_name', 'department', 'designation']
        serializer = DoctorSerializer(doctor, data = request.data, fields = dynamic_attributes)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Doctor updated', 'doctor': serializer.data})
        else:
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class GetCurrentTreatments(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        patient = request.GET.get('patient', None)
        doctor = request.GET.get('doctor', None)

# class DoctorTreatmentsListView(generics.RetrieveAPIView):
#     def get(self, request, *args, **kwargs):
#         # Get ongoing treatments for the doctor
#         doctor = request.GET.get('doctor', None)
#         patient = request.GET.get('patient', None)
#         ongoing_treatments = Treatment.objects.filter(
#             Q(doctor__user__username = doctor) | Q(sharetreatment__doctor__user__username = doctor),
#             patient__user__username = patient
#         )

#         # Serialize the treatments
#         serializer = TreatmentSerializer(ongoing_treatments, many=True)
#         serialized_data = serializer.data

#         return Response(serialized_data)

class DoctorTreatmentsListView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        # Get doctor username from request query parameters
        doctor_username = request.GET.get('doctor', None)

        # If patient field is blank, fetch all treatments for the doctor
        if not doctor_username:
            return Response({'error': 'Doctor username is required'}, status=400)

        # Get treatments based on whether patient field is provided or not
        if 'patient' in request.GET and request.GET['patient']:
            # Get treatments for a specific patient
            patient_username = request.GET.get('patient')
            print(doctor_username)
            print(patient_username)
            treatments = Treatment.objects.filter(
                Q(doctor__user__username=doctor_username) | Q(sharetreatment__doctor__user__username=doctor_username),
                patient__user__username=patient_username
            )
        else:
            # Get all treatments for the doctor
            treatments = Treatment.objects.filter(
                Q(doctor__user__username=doctor_username) | Q(sharetreatment__doctor__user__username=doctor_username)
            )

        # Serialize the treatments
        serializer = TreatmentSerializer(treatments, many=True)
        serialized_data = serializer.data

        return Response(serialized_data)
    
class GetTreatmentView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        doctor = request.GET.get('doctor', None)
        treatment = request.GET.get('treatment', None)
        treatment_obj = Treatment.objects.filter(id = treatment).first()
        if treatment_obj is None:
            return Response({'responseCode': 404, 'status': 'No treatment found'})
        return Response({'responseCode': 200, 'treatment': TreatmentSerializer(treatment_obj).data})
    
class CalculateRatingView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        doctor = request.GET.get('doctor', None)
        ratings = Rating.objects.filter(doctor__user__username = doctor)
        average_rating = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']

        return Response({'responseCode': 200, 'status': 'Rating calculated', 'rating': average_rating})

    
class GetNumberofPatientsView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        doctor = request.GET.get('doctor', None)
        one_year_ago = date.today() - timedelta(days=365)
        treatments_per_month = Treatment.objects.filter(doctor__user__username=doctor, last_date__gte=one_year_ago).annotate(month=ExtractMonth('start_date')).values('month').annotate(count=Count('id'))

        df = pd.DataFrame(treatments_per_month)

        all_months_df = pd.DataFrame({'month': range(1, 13)})
        df = pd.merge(all_months_df, df, how='left', on='month').fillna(0)
        df['count'] = df['count'].astype(dtype = 'int')

        # print(df)

        # Plot bar plot
        plt.figure(figsize=(10, 6))
        plt.bar(df['month'], df['count'], color='skyblue')
        plt.xlabel('Month')
        plt.ylabel('Number of patients to Doctor ' + doctor)
        plt.title('Month-wise Count of Visits to Doctor ' + doctor + '(Last Year)')
        plt.xticks(range(1, 13))  # Assuming month ranges from 1 to 12
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        plt.savefig('month wise visit to doctor.png')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        response_data = {
            'image': f'data:image/png;base64,{image_data}',
        }
        return Response({'responseCode': 200, 'response': response_data})

class GetPatientSuccessRateView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        doctor = request.GET.get('doctor', None)
        one_year_ago = date.today() - timedelta(days=365)
        doctor_treatments = Treatment.objects.filter(doctor__user__username=doctor, last_date__gte=one_year_ago).values('disease').annotate(success_count=Count('id', filter=Q(status='success')), failure_count=Count('id', filter=Q(status='failure')), ongoing_count=Count('id', filter=Q(status='ongoing')))
        
        columns = ['disease', 'success_count', 'failure_count', 'ongoing_count']
        data = doctor_treatments.values_list(*columns)
        df = pd.DataFrame(data, columns = columns)
        # print(df)
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
            'image': f'data:image/png;base64,{image_data}',
        }
        return Response({'responseCode': 200, 'response': response_data})