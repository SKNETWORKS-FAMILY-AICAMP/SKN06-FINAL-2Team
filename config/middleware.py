from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """로그인이 필요한 URL에 대해 로그인 체크"""
    def __init__(self, get_response):
        self.get_response = get_response
        # 로그인 체크가 필요한 URL 리스트
        self.protected_paths = (         
            '/baisc_chatbot/',
            '/romance_chatbot/',
            '/rofan_chatbot/',
            '/hero_chatbot/',
            '/historical_chatbot/',         
        )

    def __call__(self, request):
        # 요청 경로가 보호된 URL 중 하나로 시작하고, 로그인이 안 된 경우 로그인 페이지로 리디렉트
        if any(request.path.startswith(path) for path in self.protected_paths) and not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)