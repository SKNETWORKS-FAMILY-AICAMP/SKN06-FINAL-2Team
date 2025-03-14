from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db import connection
from django.http import JsonResponse

import logging
from .models import User, PresetContents, Preset
from .forms import SignUpForm, EditInformationForm
from .preset_preference import analyze_user_preference

logger = logging.getLogger(__name__)


# 회원 가입
def user_signup(request):
    if request.method == "GET":
        return render(request, "account/signup.html", {"form": SignUpForm()})
    elif request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("account:preset_preference")
        else:
            return render(request, "account/signup.html", {"form": form})


# 로그인
def user_login(request):
    if request.method == "GET":
        return render(request, "account/login.html", {"form": AuthenticationForm()})
    elif request.method == "POST":
        username_or_email = request.POST.get("username_or_email")  # 아이디 또는 이메일
        password = request.POST.get("password")

        # 이메일인지 닉네임인지 구분하여 처리
        # user = None
        # username_or_email =None

        # 이메일
        if "@" in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                username = None
        # 닉네임
        else:
            username = username_or_email

        user = authenticate(request, username=username, password=password)

        # 비밀번호 인증
        if user is not None:
            login(request, user)
            logger.info(f"로그인 성공: {user.username}")
            return redirect("chatbot:basic_chatbot")

        else:
            return render(
                request,
                "account/login.html",
                {
                    "form": AuthenticationForm(),
                    "error_msg": "아이디나 비밀번호를 다시 확인해주세요.",
                },
            )


# 로그아웃
@login_required
def user_logout(request):
    print("logout")
    logout(request)
    return redirect("chatbot:basic_chatbot_na")


# 회원 정보 조회
@login_required
def user_information(request):
    object = User.objects.get(pk=request.user.pk)
    return render(request, "account/user_information.html", {"user": object})

# 회원 정보 수정
# @login_required
def edit_information(request):
    if request.method == "POST":
        form = EditInformationForm(request.POST, instance=request.user)
        if form.is_valid():
            # 이메일과 아이디는 기존 값 유지
            form.instance.email = request.user.email
            form.instance.username = request.user.username 
            form.save()
            return redirect("account:user_information")
    else:
        form = EditInformationForm(instance=request.user)

    return render(request, "account/edit_information.html", {"form": form})

# 비밀번호 변경
@login_required
def edit_pwd(request):
    http_method = request.method
    if http_method == "GET":
        form = PasswordChangeForm(user=request.user)
        return render(request, "account/edit_pwd.html", {"form": form})
    elif http_method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(reverse("account:detail"))
        else:
            return render(
                request,
                "account/edit_pwd.html",
                {"form": form, "error_msg": "유효하지 않은 비밀번호입니다."},
            )


# 회원 탈퇴
@login_required
def user_delete(request):
    request.user.delete()
    logout(request)
    return redirect(reverse("basic_chatbot_na"))


def preset_preference(request):
    if request.method == "GET":
        contents = PresetContents.objects.values("id", "title", "thumbnail")

        works = list(contents)

        return render(request, "account/preset_preference.html", {"works": works})

    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

        user = request.user  # 현재 로그인한 사용자
        selected_works = request.POST.getlist("works")

        if not selected_works:
            return JsonResponse({"error": "작품을 선택해주세요."}, status=400)

        persona_text = analyze_user_preference(selected_works)

        if not persona_text:
            return JsonResponse({"error": "사용자 분석에 실패했습니다."}, status=500)

        Preset.objects.update_or_create(
            account_id=user, defaults={"persona_type": persona_text}
        )

        return JsonResponse(
            {"message": "저장 완료", "redirect": "/chatbot/basic_chatbot/"}
        )
