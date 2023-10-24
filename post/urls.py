from django.urls import path
from .views import (RegisterUserView, PostListCreateView, PostDetailUpdateDeleteView, CreatePostView, CreateLikeView,
                    DeleteLikeView, LikeAnalyticsView, UserActivityView)


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('posts/', PostListCreateView.as_view(), name='post_list'),
    path('posts/<int:pk>/', PostDetailUpdateDeleteView.as_view(), name='post_detail_update_delete'),
    path('create_post/', CreatePostView.as_view(), name='create_post'),
    path('like/', CreateLikeView.as_view(), name='create_like'),
    path('unlike/<int:post_id>/', DeleteLikeView.as_view(), name='delete_like'),
    path('analytics/', LikeAnalyticsView.as_view(), name='like_analytics'),
    path('user_activity/<int:user_id>/', UserActivityView.as_view(), name='user_activity'),
]
