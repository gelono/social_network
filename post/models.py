from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_text = models.TextField()
    post_creation = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', through='Like')

    def __str__(self):
        return f"Post by {self.user.username} at {self.post_creation}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like from {self.user.username} to post created at {self.post.post_creation}"


class LastStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True, blank=True)
    last_request = models.DateTimeField(null=True, blank=True)
