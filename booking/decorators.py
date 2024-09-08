from rest_framework.response import Response
from django.contrib.auth.models import AnonymousUser


def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return Response(status=404)
        return func(self, request, *args, **kwargs)
    return wrapper
