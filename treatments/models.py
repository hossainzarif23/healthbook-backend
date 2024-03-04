from django.db import models
from doctors.models import Doctor
from patients.models import Patient

# Create your models here.

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
)

TREATMENT_STATUS_CHOICES = (
    ('ongoing', 'Ongoing'),
    ('success', 'Success'),
    ('failure', 'Failure'),
)

MEAL_TIME_CHOICES = [
    ('before', 'Before'),
    ('after', 'After'),
]

TREATMENT_VERIFICATION_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

class Request(models.Model):
    patient = models.ForeignKey(Patient, on_delete= models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete= models.CASCADE)
    status = models.CharField(max_length = 20, default = 'pending', choices = STATUS_CHOICES)
    date = models.DateField(auto_now_add = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['patient', 'doctor'], name = 'unique_patient_doctor_date'),
        ]

class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete= models.CASCADE)
    doctor = models.ForeignKey(Doctor, null = True, on_delete= models.SET_NULL)
    doctor_name = models.CharField(max_length = 50, null = True)
    speciality = models.CharField(max_length = 50, null = True)
    designation = models.CharField(max_length = 50, null = True)
    hospital_name = models.CharField(max_length = 50, null = True)
    disease = models.CharField(max_length = 100, null = True, blank = True)
    status = models.CharField(max_length = 20, default = 'ongoing', choices = TREATMENT_STATUS_CHOICES)
    start_date = models.DateField()
    last_date = models.DateField()
    verified = models.CharField(max_length = 5, null = True, choices = TREATMENT_VERIFICATION_CHOICES)
    cost = models.IntegerField(null = True, default = 0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['patient', 'doctor', 'disease', 'start_date'], name = 'unique_patient_doctor_disease_start_date')
        ]
        ordering = ['-last_date']

class Prescription(models.Model):
    age = models.IntegerField()
    weight = models.IntegerField()
    height = models.IntegerField(null = True)
    address = models.CharField(max_length = 255)
    bp_low = models.IntegerField()
    bp_high = models.IntegerField()
    next_appointment = models.IntegerField(null = True)
    notes = models.CharField(max_length = 255, null = True, blank = True)
    treatment = models.ForeignKey(Treatment, on_delete = models.CASCADE, null = True, blank = True)
    date = models.DateField()

    class Meta:
        ordering = ['-date']

class Symptom(models.Model):
    prescription = models.ForeignKey(Prescription, related_name = 'symptoms', on_delete = models.CASCADE)
    symptom = models.CharField(max_length = 255)

    class Meta:
        # Define a unique constraint for prescription and symptom fields
        constraints = [
            models.UniqueConstraint(fields = ['prescription', 'symptom'], name = 'unique_prescription_symptom')
        ]

class Test(models.Model):
    prescription = models.ForeignKey(Prescription, related_name = 'tests', on_delete = models.CASCADE)
    test_name = models.CharField(max_length = 255)
    image_path = models.CharField(max_length = 255, null = True, blank = True)

    class Meta:
        # Define a unique constraint for prescription and test_name fields
        constraints = [
            models.UniqueConstraint(fields=['prescription', 'test_name'], name='unique_prescription_test_name')
        ]

class Diagnosis(models.Model):
    prescription = models.ForeignKey(Prescription, related_name = 'diagnoses', on_delete = models.CASCADE)
    disease = models.CharField(max_length = 255)

    class Meta:
        # Define a unique constraint for prescription and disease fields
        constraints = [
            models.UniqueConstraint(fields=['prescription', 'disease'], name='unique_prescription_disease')
        ]

class Advice(models.Model):
    prescription = models.ForeignKey(Prescription, related_name = 'advices', on_delete = models.CASCADE)
    advice = models.CharField(max_length = 255)

    class Meta:
        # Define a unique constraint for prescription and advice fields
        constraints = [
            models.UniqueConstraint(fields=['prescription', 'advice'], name='unique_prescription_advice')
        ]

class Medicine(models.Model):
    prescription = models.ForeignKey(Prescription, related_name = 'medicines', on_delete = models.CASCADE)
    medicine_name = models.CharField(max_length = 255)
    duration = models.IntegerField()
    interval = models.IntegerField(null = True, blank = True)
    meal_time = models.CharField(max_length = 6, choices = MEAL_TIME_CHOICES, null = True, blank = True)
    breakfast = models.BooleanField(default = False)
    lunch = models.BooleanField(default = False)
    dinner = models.BooleanField(default = False)

class PrescriptionAccess(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete = models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete = models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete = models.CASCADE)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['prescription', 'doctor'], name = 'unique_prescription_doctor')
        ]

class ShareTreatment(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete = models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete = models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['treatment', 'doctor'], name = 'unique_treatment_doctor')
        ]