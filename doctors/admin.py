from django.contrib import admin
from .models import Hospital, Doctor, Clinic, Consultency, ConsultencyDay, Degree

# Register your models here.
models_list = [Hospital, Doctor, Clinic, Consultency, ConsultencyDay, Degree]
admin.site.register(models_list)
