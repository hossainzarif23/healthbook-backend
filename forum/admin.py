from django.contrib import admin
from .models import Post, Comment, Topic, UpvotePost, UpvoteComment, ReportPost, ReportComment

# Register your models here.
model_list = [Post, Comment, Topic, UpvotePost, UpvoteComment, ReportPost, ReportComment]
admin.site.register(model_list)
