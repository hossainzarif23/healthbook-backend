from django.db import models
from users.models import User

# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(max_length = 50, null = False)
    area = models.CharField(max_length = 30, null = True)
    dob = models.DateField(null = False)