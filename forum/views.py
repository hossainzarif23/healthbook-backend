from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from .models import Post, Comment, Topic, UpvotePost, UpvoteComment, ReportPost, ReportComment, Image, CoverImage, ReportPost, ReportComment
from .serializers import PostSerializer, UpvotePostSerializer, CommentSerializer, UpvoteCommentSerializer, UpdatePostSerializer, ImageSerializer, CoverImageSerializer, ReportPostSerializer, ReportCommentSerializer
from patients.models import Patient
from users.models import User

from django.http.response import JsonResponse
from django.utils.dateparse import parse_date

from rest_framework.parsers import MultiPartParser, FormParser

from django.db.models import Count
import base64

# Create your views here.
class CreatePostView(generics.CreateAPIView):
    # parser_class = (MultiPartParser, FormParser)
    def post(self, request, format = None, *args, **kwargs):
        data = request.data
        print(data)
        # print(data.get('img', None))
        author = data.get('author', None)
        title = data.get('title', None)
        content = data.get('content', None)
        topics = data.get('topics', None)

        print(author)
        print(title)
        print(content)
        print(topics)

        dynamic_attributes = ['author', 'title', 'content', 'topics']
        user = User.objects.filter(username = author).first()
        if user is None:
            return Response({'responseCode': 404, 'status': 'No such user exists'})
        patient = Patient.objects.filter(user__username = author).first()
        if patient is not None:
            return Response({'responseCode': 400, 'status': 'Posting is not permitted for patients'})
        serializer = PostSerializer(data = {
            "author": author,
            "title": title,
            "content": content,
            "topics": topics
        }, fields = dynamic_attributes)
        if serializer.is_valid():
            serializer.save()
            print(serializer.instance.id)
            return Response({'responseCode': 200, 'status': 'Post uploaded successfully', 'post_id': serializer.instance.id})

        return Response({'responseCode': 400, 'status': serializer.errors})
    
class UpdatePostView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        author = request.data.get('author', None)
        post = Post.objects.filter(pk = id, author = author).first()
        if post is None:
            return Response({'responseCode': 400, 'status': 'Post doesnt exist'})
        serializer = UpdatePostSerializer(post, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Post updated successfully'})
        return Response({'responseCode': 400, 'status': serializer.errors})
    
class DeletePostView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        author = request.data.get('author', None)
        post = Post.objects.filter(pk = id, author = author).first()
        if post is None:
            return Response({'responseCode': 400, 'status': 'Post doesnt exist'})
        post.delete()
        return Response({'responseCode': 200, 'status': 'Post deleted successfully'})
    
class GetPostView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        id = request.GET.get('id', None)
        post = Post.objects.filter(pk = id).first()
        print(post.author)
        post = PostSerializer(post).data
        return Response({'responseCode': 200, 'post': post})
    
class SearchPostsView(generics.RetrieveAPIView):
    def post(self, request, *args, **kwargs):
        author = request.data.get('author', None)
        title = request.data.get('title', None)
        topics = request.data.get('topics', None)
        posts = Post.objects.all()
        if author is not None:
            posts = posts.filter(author__username = author)
        if title is not None:
            posts = posts.filter(title__icontains = title)
        if topics is not None:
            posts = posts.filter(id__in=Topic.objects.filter(topic_name__in=topics).values_list('post_id'))
        if len(posts) > 0:
            return Response({'responseCode': 200, 'post': PostSerializer(posts, many = True, fields = ['id', 'author', 'title', 'content', 'date', 'topics', 'upvotes', 'downvotes', 'cover_images']).data})
        else:
            return Response({'responseCode': 404, 'status': 'No posts found'})
        
class UpvoteorDownvotePostView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        post = request.data.get('post', None)
        upvote_downvote = UpvotePost.objects.filter(user = user, post = post).first()
        if upvote_downvote is not None:
            return Response({'responseCode': 400, 'status': 'Already upvoted/downvoted'})
        serializer = UpvotePostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Upvote completed'})
        return Response({'responseCode': 400, 'status': serializer.errors})
    
class AddCommentView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = CommentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Comment added'})
        return Response({'responseCode': 400, 'status': serializer.errors})
    
class DeleteCommentView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        author = request.data.get('author', None)
        comment_id = request.data.get('comment_id', None)
        comment = Comment.objects.filter(author = author, pk = comment_id).first()
        if comment is None:
            return Response({'responseCode': 404, 'status': 'Not allowed to delete the comment'})
        comment.delete()
        return Response({'responseCode': 200, 'status': 'Comment deleted'})
    
class UpdateCommentView(generics.UpdateAPIView):
    def patch(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        author = request.data.get('author', None)
        comment = Comment.objects.filter(pk = id).first()
        if comment is None:
            return Response({'responseCode': 404, 'status': 'No comment found'})
        if comment.author.username != author:
            return Response({'responseCode': 400, 'status': 'Not allowed to update others comment'})
        serializer = CommentSerializer(comment, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Comment updated'})
        return Response({'responseCode': 400, 'status': serializer.errors})
    
class UpvoteorDownvoteCommentView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        comment = request.data.get('comment', None)
        upvote_downvote = UpvoteComment.objects.filter(user = user, comment = comment).first()
        if upvote_downvote is not None:
            return Response({'responseCode': 400, 'status': 'Already upvoted/downvoted'})
        serializer = UpvoteCommentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Upvote completed'})
        return Response({'responseCode': 400, 'status': serializer.errors})
    
class DeleteUpvoteorDownvotePostView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        id = request.data.get('id', None)
        post = request.data.get('post', None)
        upvote_or_downvote = UpvotePost.objects.filter(user = user, pk = id, post = post).first()
        if upvote_or_downvote is None:
            return Response({'responseCode': 400, 'response': 'Not allowed to delete upvote/downvote'})
        upvote_or_downvote.delete()
        return Response({'responseCode': 200, 'response': 'upvote or downvote deleted'})
    
class DeleteUpvoteorDownvoteCommentView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        user = request.data.get('user', None)
        id = request.data.get('id', None)
        comment = request.data.get('comment', None)
        upvote_or_downvote = UpvoteComment.objects.filter(user = user, pk = id, comment = comment).first()
        if upvote_or_downvote is None:
            return Response({'responseCode': 400, 'response': 'Not allowed to delete upvote/downvote'})
        upvote_or_downvote.delete()
        return Response({'responseCode': 200, 'response': 'upvote or downvote deleted'})
    
class AddImageToPostView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    def create(self, request, format = None, *args, **kwargs):
        print(request.data)
        serializer = ImageSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Image added'})
        else:
            return Response({'responseCode': 400, 'status': serializer.errors})
        
class AddCoverImageToPostView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    def create(self, request, format = None, *args, **kwargs):
        print(request.data)
        serializer = CoverImageSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Cover Image added'})
        else:
            return Response({'responseCode': 400, 'status': serializer.errors})

class ReportPostView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = ReportPostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Post reported'})
        return Response({'responseCode': 400, 'status': serializer.errors})
    
class DeleteReportPostView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        report = ReportPost.objects.filter(pk = id).first()
        if report is None:
            return Response({'responseCode': 400, 'status': 'No such report exists'})
        report.delete()
        return Response({'responseCode': 200, 'status': 'Report deleted'})

class ReportCommentView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = ReportCommentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'responseCode': 200, 'status': 'Comment reported'})
        return Response({'responseCode': 400, 'status': serializer.errors})