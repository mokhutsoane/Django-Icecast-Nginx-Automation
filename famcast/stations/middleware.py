from django.http import HttpResponseForbidden
from django.conf import settings

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key != settings.API_KEY:
            return HttpResponseForbidden('Invalid API key')
        return self.get_response(request)
