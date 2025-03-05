from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from .models import User
from .forms import SignUpForm, EditInformationForm


# 회원 가입
def user_signup(request):
    if request.method == "GET":
        return render(
            request, "account/signup.html", {"form": SignUpForm()}
        )
    elif request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("basic_chatbot"))
        else:
            return render(request, "account/signup.html", {"form": form})

# 로그인
def user_login(request):
    if request.method == "GET":
        return render(request, "account/login.html", {"form": AuthenticationForm()})
    elif request.method == "POST":
        username_or_email = request.POST.get("user_id")  # 아이디 또는 이메일
        password = request.POST.get("password")
        
        # 이메일인지 닉네임인지 구분하여 처리
        user = None

        # 이메일
        if "@" in username_or_email:  
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                user = None
        # 닉네임
        else:
            user = User.objects.filter(username=username_or_email).first()

        # 비밀번호 확인
        if user is not None and authenticate(request, username=username, password=password):
            login(request, user)
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            else:
                return redirect(reverse("basic_chatbot"))
        else:
            return render(
                request,
                "account/login.html",
                {
                    "form": AuthenticationForm(),
                    "error_msg": "유효하지 않은 계정입니다.",
                },
            )

# 로그아웃
@login_required
def user_logout(request):
    print("logout")
    logout(request)
    return redirect(reverse("basic_chatbot_na"))

# 회원 정보 조회
@login_required
def user_information(request):
    object = User.objects.get(pk=request.user.pk)
    return render(request, "account/user_inforamtion.html", {"user": object})

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
