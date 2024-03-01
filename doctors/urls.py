from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.DoctorSignupView.as_view()),
    path('login', views.DoctorLoginView.as_view()),
    path('profile', views.DoctorProfileView.as_view()),
    path('add-degree', views.AddDegreeView.as_view()),
    path('list-of-degrees', views.ListofDegreesView.as_view()),
    path('add-consultency', views.AddConsultencyView.as_view()),
    path('request-data', views.RequestPatientData.as_view()),
    path('add-treatment', views.CreateTreatmentView.as_view()),
    path('update-treatment', views.UpdateTreatmentView.as_view()),
    path('upload-prescription', views.UploadPrescriptionView.as_view()),
    path('request-prescription-access', views.PrescriptionAccessCreateView.as_view()),
    path('get-prescription', views.GetPrescriptionView.as_view()),
    path('patient', views.PatientSearchAPI.as_view()),
    path('get-list-of-prescriptions', views.GetListofprescriptionView.as_view()),
    path('current-medicines', views.GetCurrentMedicinesView.as_view()),
    path('current-diseases', views.GetCurrentDiseaseView.as_view()),
    path('profile-update', views.DoctorProfileUpdateView.as_view()),
    path('patient-treatments', views.DoctorTreatmentsListView.as_view()),
    path('get-treatment', views.GetTreatmentView.as_view()),
    # path('patient', views.DoctorTreatmentsListView.as_view()),
    path('number-of-patients', views.GetNumberofPatientsView.as_view()),
    path('patient-success-rate', views.GetPatientSuccessRateView.as_view()),
    path('rating', views.CalculateRatingView.as_view()),
]