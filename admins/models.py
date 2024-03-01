from django.db import models
from users.models import User
from doctors.models import Doctor

# Create your models here.

ACTION_CHOICES = (
    ('verify', 'Verify'),
    ('delete', 'Delete')
)

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)

class DoctorVerification(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete = models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete = models.CASCADE)
    time = models.DateTimeField(auto_now_add = True)
    action = models.CharField(max_length = 10, default = 'verify', choices = ACTION_CHOICES)