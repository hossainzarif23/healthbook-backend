from django.db import models
from users.models import User
from patients.models import Patient

# Create your models here.

DESIGNATION_CHOICES = (
    ('consultant', 'Consultant'),
    ('senior_consultant', 'Senior Consultant'),
    ('assistant_professor', 'Assistant Professor'),
    ('associate_professor', 'Associate Professor'),
    ('professor', 'Professor'),
)

DAY_CHOICES = (
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday')
)

RATING_CHOICES = [(i, i) for i in range(1, 6)]

class Hospital(models.Model):
    name = models.CharField(max_length = 100, null = False)
    area = models.CharField(max_length = 30, null = False)

class Clinic(models.Model):
    name = models.CharField(max_length = 100, null = False)
    area = models.CharField(max_length = 30, null = False)

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(max_length = 50, null = False)
    area = models.CharField(max_length = 30, null = True)
    dob = models.DateField(null = False)
    description = models.CharField(max_length = 400, null = True)
    hospital = models.ForeignKey(Hospital, on_delete = models.CASCADE)
    department = models.CharField(max_length = 30, null = False)
    designation = models.CharField(max_length = 25, choices = DESIGNATION_CHOICES)
    verified = models.BooleanField(default = False)

class Degree(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='degree')
    degree = models.CharField(max_length = 10, null = False)
    speciality = models.CharField(max_length= 20, null = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['doctor', 'degree', 'speciality'], name = 'unique_doctor_degree_speciality')
        ]

class Consultency(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete= models.CASCADE, related_name='consultency')
    clinic = models.ForeignKey(Clinic, on_delete= models.CASCADE)
    room = models.CharField(max_length = 4)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['doctor', 'clinic', 'room'], name='unique_doctor_clinic_room'),
        ]

class ConsultencyDay(models.Model):
    consultency = models.ForeignKey(Consultency, on_delete = models.CASCADE, related_name='days')
    day = models.CharField(max_length = 10, choices = DAY_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['consultency', 'day'], name='unique_consultency_day'),
        ]

class Rating(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete = models.CASCADE, choices = RATING_CHOICES)
    rating = models.IntegerField(choices = RATING_CHOICES)
    patient = models.ForeignKey(Patient, on_delete = models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['doctor', 'patient'], name='unique_doctor_patient')
        ]