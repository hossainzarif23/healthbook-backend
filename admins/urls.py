from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login', views.AdminLoginView.as_view()),
    path('getDoctors', views.GetUnverifiedDoctors.as_view()),
    path('verifyDoctor', views.DoctorVerificationView.as_view()),
    path('deleteDoctor', views.DoctorDeleteView.as_view()),
]