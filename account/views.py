from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from .models import User
from .forms import SignUpForm, EditInformationForm


# 사용자 가입
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

# 사용자 로그인
def user_login(request):
    if request.method == "GET":
        return render(request, "account/login.html", {"form": AuthenticationForm()})
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
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
                    "error_msg": "아이디나 비밀번호를 다시 확인해주세요.",
                },
            )

# 사용자 로그아웃
@login_required
def user_logout(request):
    print("logout")
    logout(request)
    return redirect(reverse("chat"))

# 사용자 정보 조회
@login_required
def user_detail(request):
    object = User.objects.get(pk=request.user.pk)
    return render(request, "account/detail.html", {"user": object})

# 사용자 비밀번호 변경
@login_required
def pwd_change(request):
    http_method = request.method
    if http_method == "GET":
        form = PasswordChangeForm(user=request.user)
        return render(request, "account/pwd_change.html", {"form": form})
    elif http_method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(reverse("account:detail"))
        else:
            return render(
                request,
                "account/pwd_change.html",
                {"form": form, "error_msg": "유효하지 않은 비밀번호입니다."},
            )

# 사용자 정보 수정
@login_required
def user_update(request):
    if request.method == "GET":
        object = User.objects.get(pk=request.user.pk)
        form = EditInformationForm(instance=object)
        return render(request, "account/update.html", {"form": form})
    elif request.method == "POST":
        object = User.objects.get(pk=request.user.pk)
        form = EditInformationForm(request.POST, request.FILES, instance=object)
        if form.is_valid():
            form.save()
            return redirect(reverse("account:detail"))
        else:
            return render(request, "account/update.html", {"form": form})

# 사용자 탈퇴
@login_required
def user_delete(request):
    request.user.delete()
    logout(request)
    return redirect(reverse("chat"))
