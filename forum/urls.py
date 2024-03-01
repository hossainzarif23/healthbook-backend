from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('create-post', views.CreatePostView.as_view()),
    path('update-post', views.UpdatePostView.as_view()),
    path('delete-post', views.DeletePostView.as_view()),
    path('load-post', views.GetPostView.as_view()),
    path('list-of-posts', views.SearchPostsView.as_view()),
    path('upvote-downvote', views.UpvoteorDownvotePostView.as_view()),
    path('add-comment', views.AddCommentView.as_view()),
    path('delete-comment', views.DeleteCommentView.as_view()),
    path('update-comment', views.UpdateCommentView.as_view()),
    path('upvote-downvote-comment', views.UpvoteorDownvoteCommentView.as_view()),
    path('delete-upvote-downvote', views.DeleteUpvoteorDownvotePostView.as_view()),
    path('delete-upvote-downvote-comment', views.DeleteUpvoteorDownvoteCommentView.as_view()),
]