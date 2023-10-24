from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Like, LastStatistics


class UserSerializer(serializers.ModelSerializer):
    """
    This class is used to register a new user
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        LastStatistics.objects.create(user=user)
        return user


class BasePostSerializer(serializers.ModelSerializer):
    """
    This basic serializer for processing publications
    """
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return obj.likes.count()

    class Meta:
        model = Post
        fields = ('id', 'user', 'post_text', 'post_creation', 'likes')


class PostSerializer(BasePostSerializer):
    """
    This class is used to provide general information about publications
    """
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username

    class Meta(BasePostSerializer.Meta):
        fields = ('id', 'username', 'post_text', 'post_creation', 'likes')


class PostAdminSerializer(BasePostSerializer):
    """
    This class is used to process information by the administrator
    """
    class Meta(BasePostSerializer.Meta):
        fields = ('id', 'user', 'post_text', 'post_creation', 'likes')
        extra_kwargs = {'post_creation': {'read_only': False}}


class PostCreateSerializer(serializers.ModelSerializer):
    """
    This class is used to create a new publication
    """
    class Meta:
        model = Post
        fields = ('post_text', )

    def create(self, validated_data):
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)

        return post


class LikeSerializer(serializers.ModelSerializer):
    """
    This class is used to validate and create a new like
    """
    class Meta:
        model = Like
        fields = ('post', )

    def validate(self, data):
        user = self.context['request'].user
        post = data.get('post')

        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError('You have already liked this post')

        return data
