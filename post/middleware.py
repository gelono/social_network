from django.utils import timezone
from post.models import LastStatistics


class UpdateLastRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user

        if user.is_authenticated:
            user_stat = LastStatistics.objects.get(user=user)
            user_stat.last_request = timezone.now()
            user_stat.save()

        return response
