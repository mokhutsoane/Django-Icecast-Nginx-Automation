from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

class ApiKeyBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key == settings.API_KEY:
            return AnonymousUser()
