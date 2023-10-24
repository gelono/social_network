from rest_framework import generics, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsAdminOrReadOnly, IsAdminOrPostOwner
from .serializers import UserSerializer, PostSerializer, PostCreateSerializer, PostAdminSerializer, LikeSerializer
from rest_framework.decorators import permission_classes, authentication_classes
from .models import Post, Like, LastStatistics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.timezone import make_aware
from datetime import datetime
from django.db import models
from rest_framework.authtoken.views import ObtainAuthToken
from django.utils import timezone


@authentication_classes([])
@permission_classes([])
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostListCreateView(generics.ListCreateAPIView):
    """
    This View is used to display the entire list of publications
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly, ]


class PostDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    This View is used for CRUD operations on a specific publication
    """
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrPostOwner]

    def get_serializer_class(self):
        # Getting particular serializer
        if self.request.user.is_staff:
            return PostAdminSerializer
        return PostSerializer


class CreatePostView(generics.CreateAPIView):
    """
    This View is used to create a new publication
    """
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated, ]


class CreateLikeView(generics.CreateAPIView):
    """
    This View is used to create a new like
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DeleteLikeView(generics.DestroyAPIView):
    """
    This View is used to delete a previously placed like.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'post_id'

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        post_id = self.kwargs['post_id']
        try:
            like = Like.objects.get(user=user, post_id=post_id)
            self.perform_destroy(like)
            return Response({'detail': 'Like removed successfully.'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'detail': 'Like not found.'}, status=status.HTTP_404_NOT_FOUND)


class LikeAnalyticsView(APIView):
    """
    This View is used to obtain aggregated statistics on the number of likes by day
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # parse dates and convert them to datetime, taking into account the time zone
        date_from = make_aware(datetime.strptime(date_from, '%Y-%m-%d'))
        date_to = make_aware(datetime.strptime(date_to, '%Y-%m-%d'))

        # get aggregated statistics
        likes_data = Like.objects.filter(
            like_creation__date__gte=date_from,
            like_creation__date__lte=date_to
        ).values('like_creation__date').annotate(likes_count=models.Count('id'))

        return Response(likes_data)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    This View is used to authenticate the user and record login time
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            user_stat = LastStatistics.objects.get(user=user)
            user_stat.last_login = timezone.now()
            user_stat.save()

        return response


class UserActivityView(APIView):
    """
    This View is used to obtain user statistics on the time of interaction with the resource
    """
    permission_classes = [IsAdminUser]
    lookup_url_kwarg = 'user_id'

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user_stat = LastStatistics.objects.get(user_id=user_id)

        return Response({'username': user_stat.user.username,
                         'last_login': user_stat.last_login,
                         'last_request': user_stat.last_request})
