from django.contrib import admin
from .models import User

# Register your models here.
models_list = [User]
admin.site.register(models_list)