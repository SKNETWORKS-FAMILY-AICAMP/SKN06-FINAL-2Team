from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db import connection
from django.http import JsonResponse

import logging
from .models import User
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
@login_required
def edit_information(request):
    if request.method == "GET":
        object = User.objects.get(pk=request.user.pk)
        form = EditInformationForm(instance=object)
        return render(request, "account/edit_information.html", {"form": form})
    elif request.method == "POST":
        object = User.objects.get(pk=request.user.pk)
        form = EditInformationForm(request.POST, request.FILES, instance=object)
        if form.is_valid():
            form.save()
            return redirect(reverse("account:detail"))
        else:
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


# 최초 취향 분석
def preset_preference(request):
    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, thumbnail FROM preset_preference_contents"
            )
            contents = cursor.fetchall()

        # 딕셔너리 리스트로 변환
        works = [
            {"id": work[0], "title": work[1], "thumbnail": work[2]} for work in contents
        ]

        return render(request, "account/preset_preference.html", {"works": works})

    elif request.method == "POST":
        if not request.user.is_authenticated:  # 로그인 여부
            return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

        selected_works = request.POST.getlist("works")

        if not selected_works:
            return JsonResponse({"error": "작품을 선택해주세요."}, status=400)

        # 현재 로그인한 회원의 ID 가져오기
        account_id = request.user.id
        logger.debug(f"사용자 ID {account_id}님이 선호하는 작품을 선택 중입니다.")

        if not isinstance(account_id, int):  # 정수형이 아니면 변환
            account_id = int(account_id)

        # 'persona_type' 분석
        persona_data = analyze_user_preference(selected_works)

        if not persona_data:
            return JsonResponse({"error": "사용자 분석에 실패했습니다."}, status=500)

        # `preset_preference_account` 테이블에 데이터 저장
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO preset_preference_account (account_id, persona_type) VALUES (%s, %s)",
                [account_id, persona_data],
            )

        return JsonResponse(
            {"message": "저장 완료", "redirect": "/chatbot/basic_chatbot/"}
        )
