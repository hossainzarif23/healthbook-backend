from django.contrib import admin
from .models import Patient

# Register your models here.
models_list = [Patient]
admin.site.register(models_list)