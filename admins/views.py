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
from patients.models import Patient
from treatments.models import Treatment, Prescription
from forum.models import ReportPost, ReportComment
from forum.serializers import ReportPostSerializer, ReportCommentSerializer
from doctors.serializers import DoctorSerializer

from django.http import HttpResponse

from django.db.models import Count, Q

import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import base64
from io import BytesIO

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
        
class GetTreatmentsData(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        # print(request.GET)
        area = request.GET.get('area', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        username = request.GET.get('username', None)

        admin = Admin.objects.filter(user__username=username).first()

        if admin is None:
            return Response({'responseCode': 400, 'status': 'Not allowed to access this data'})

        print(area, start_date, end_date)
        treatments = Treatment.objects.filter(
            patient__area=area,
            start_date__range=(start_date, end_date)
        ).select_related('patient')

        print(treatments)

        headers = ['id', 'Disease', 'Status', 'Hospital Name', 'Start Date', 'Last Date', 'Cost']

        csv_filename = 'treatments_' + area + '_' + start_date + '_' + end_date + '.csv'

        # Write data to CSV file
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Write headers to CSV file
            for treatment in treatments:
                # Write treatment data to CSV file
                writer.writerow([
                    treatment.patient.id,
                    treatment.disease,
                    treatment.status,
                    treatment.hospital_name,
                    treatment.start_date,
                    treatment.last_date,
                    treatment.cost
                ])
        
        with open(csv_filename, 'rb') as csv_file:
            response = HttpResponse(csv_file.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={csv_filename}'
            return response
        
class PostReportsView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        reports = ReportPost.objects.all()
        return Response({'responseCode': 200, 'reports': ReportPostSerializer(reports, many = True).data})
    

class DiseaseFrequencyView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        one_year_ago = date.today() - timedelta(days=365)
        treatments = Treatment.objects.filter(last_date__gte=one_year_ago).values('disease').annotate(count=Count('id'))

        if not treatments:
            df = pd.DataFrame(columns=['disease', 'count'])
        else:
            columns = ['disease', 'count']
            data = treatments.values_list(*columns)
            df = pd.DataFrame(data, columns=columns)

        plt.figure(figsize=(8, 6))
        plt.bar(df['disease'], df['count'], color='skyblue')
        plt.xlabel('Disease')
        plt.ylabel('Count')
        plt.title("Last Year Disease Count (Last Year)")

        plt.savefig('disease_treatment_counts.png')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        response_data = {
            'image': f'data:image/png;base64,{image_data}',
        }
        return Response({'responseCode': 200, 'response': response_data})
    
class TreatmentSuccessView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        one_year_ago = date.today() - timedelta(days=365)
        treatments = Treatment.objects.filter(last_date__gte=one_year_ago).values('disease').annotate(
            success_count=Count('id', filter=Q(status='success')),
            failure_count=Count('id', filter=Q(status='failure')),
            ongoing_count=Count('id', filter=Q(status='ongoing'))
        )

        if not treatments:
            df = pd.DataFrame(columns=['disease', 'success_count', 'failure_count', 'ongoing_count'])
        else:
            columns = ['disease', 'success_count', 'failure_count', 'ongoing_count']
            data = treatments.values_list(*columns)
            df = pd.DataFrame(data, columns=columns)

        print(df)
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
    
class PatientSatisfactionView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        one_year_ago = date.today() - timedelta(days=365)
        patient_data = []
        
        for patient in Patient.objects.all():
            treatment_count= Treatment.objects.filter(patient=patient, start_date__gte=one_year_ago).count()
            prescription_count = Prescription.objects.filter(treatment__patient=patient, date__gte=one_year_ago).count()
            satisfaction_rate = 10 - 0.4 * treatment_count - 0.1 * prescription_count
            patient_data.append({'Patient_ID': patient.id, 'Satisfaction_Index': satisfaction_rate})

        df = pd.DataFrame(patient_data)

        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=df['Satisfaction_Index'], shade=True)
        plt.title('Patient Health Satisfaction Index KDE Plot')
        plt.xlabel('Satisfaction Index')
        plt.ylabel('Density')

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