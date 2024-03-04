from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login', views.AdminLoginView.as_view()),
    path('getDoctors', views.GetUnverifiedDoctors.as_view()),
    path('verifyDoctor', views.DoctorVerificationView.as_view()),
    path('deleteDoctor', views.DoctorDeleteView.as_view()),
    path('treatments-data', views.GetTreatmentsData.as_view()),
    path('postreports', views.PostReportsView.as_view()),
    path('disease-frequency', views.DiseaseFrequencyView.as_view()),
    path('treatment-success', views.TreatmentSuccessView.as_view()),
    path('patient-satisfaction', views.PatientSatisfactionView.as_view()),
]