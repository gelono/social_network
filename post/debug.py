from django.contrib.auth.models import User
from post.models import LastStatistics

for user in User.objects.all():
    LastStatistics.objects.create(user=user)

print("All users updated.")
