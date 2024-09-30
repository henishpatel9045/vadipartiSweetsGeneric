from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser


def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return redirect(f"/admin/login/?next={request.path}")
        return func(self, request, *args, **kwargs)
    return wrapper
