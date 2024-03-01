from django.contrib import admin
from .models import Admin

# Register your models here.
models_list = [Admin]
admin.site.register(models_list)
