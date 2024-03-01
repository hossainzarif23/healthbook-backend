from rest_framework import serializers
from .models import Post, Comment, Topic, UpvotePost, UpvoteComment, ReportPost, ReportComment, Image
from users.models import User
from patients.models import Patient
from doctors.models import Doctor

class CommentSerializer(serializers.ModelSerializer):
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'content', 'date', 'upvotes', 'downvotes')

    def get_upvotes(self, obj):
        # Efficiently count upvotes using nested serializer and Subquery
        upvotes = UpvoteComment.objects.filter(comment=obj, is_upvote=1).count()
        return upvotes
    
    def get_downvotes(self, obj):
        downvotes = UpvoteComment.objects.filter(comment=obj, is_upvote=0).count()
        return downvotes

    def __init__(self, *args, **kwargs):
        # Dynamically set fields based on the 'fields' parameter
        fields = kwargs.pop('fields', None)
        super(CommentSerializer, self).__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)    

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Dynamically set fields based on the 'fields' parameter
        fields = kwargs.pop('fields', None)
        super(TopicSerializer, self).__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)    

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    topics = TopicSerializer(many=True, fields=('topic_name',), required=False)  # Allow creating/updating topics
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'content', 'date', 'comments', 'topics', 'upvotes', 'downvotes')

    def create(self, validated_data):
        topics_data = validated_data.pop('topics', [])
        post = Post.objects.create(**validated_data)
        
        for topic_data in topics_data:
            Topic.objects.create(post=post, **topic_data)
    
        return post
    
    def get_upvotes(self, obj):
        # Efficiently count upvotes using nested serializer and Subquery
        upvotes = UpvotePost.objects.filter(post=obj, is_upvote=1).count()
        return upvotes
    
    def get_downvotes(self, obj):
        downvotes = UpvotePost.objects.filter(post=obj, is_upvote=0).count()
        return downvotes

    def __init__(self, *args, **kwargs):
        # Dynamically set fields based on the 'fields' parameter
        fields = kwargs.pop('fields', None)
        super(PostSerializer, self).__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class UpvotePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpvotePost
        fields = '__all__'

class UpvoteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpvoteComment
        fields = '__all__'