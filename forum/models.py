from django.db import models
from doctors.models import Doctor
from patients.models import Patient
from users.models import User

from django.utils.translation import gettext_lazy as _

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=10000)
    date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']  # Order posts by date in descending order (latest first)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=10000)
    date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']  # Order posts by date in descending order (latest first)

class Topic(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='topics')
    topic_name = models.CharField(max_length = 50)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['post', 'topic_name'], name = 'unique_post_topic'),
        ]
        

class UpvotePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_upvote = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['user', 'post'], name = 'unique_user_post'),
        ]

class UpvoteComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    is_upvote = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['user', 'comment'], name = 'unique_user_comment')
        ]

class ReportPost(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    reason = models.CharField(max_length = 100)
    date = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-date']

class ReportComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    reason = models.CharField(max_length = 100)
    date = models.DateTimeField(auto_now_add = True)

def upload_to(instance, filename):
    return 'forum/{filename}'.format(filename = filename)

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='images')
    image_path = models.ImageField(_("Image"), upload_to = upload_to, null = True, blank = True)
    caption = models.CharField(max_length = 200, null = True, blank = True)

class CoverImage(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='cover_images')
    image_path = models.ImageField(_("Image"), upload_to = upload_to, null = True, blank = True)
    caption = models.CharField(max_length = 200, null = True, blank = True)