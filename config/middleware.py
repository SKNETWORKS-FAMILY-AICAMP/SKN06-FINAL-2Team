from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """로그인이 필요한 URL에 대해 로그인 체크"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/restricted-app/') and not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)