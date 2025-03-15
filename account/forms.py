# Form 클래스 정의
## 등록폼, 수정폼 두가지 정의

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,  # 회원 가입 폼
    UserChangeForm,  # 회원 정보 수정 폼
)
from .models import User
import re


# 회원 가입 폼
class SignUpForm(UserCreationForm):

    GENDER_CHOICE = [("남성", "남성"), ("여성", "여성")]
    gender = forms.ChoiceField(choices=GENDER_CHOICE, widget=forms.Select, label="성별")

    class Meta:
        model = User
        # form field에 명시할 항목
        fields = [
            "name",
            "username",
            "email",
            "password1",
            "password2",
            "birthday",
            "gender",
        ]

        # Input type을 변경.
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

    # 이름 형식 제한
    ## 조건
    ## 1. 2자 이상
    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 2:
            raise forms.ValidationError("2자 이상 입력하세요.")
        return name

    # 닉네임 형식 제한
    ## 조건
    ## 1. 5자 이상
    ## 2. 특수문자 사용 불가능
    def clean_username(self):
        username = self.cleaned_data["username"]
        if len(username) < 5:
            raise forms.ValidationError("5자 이상 입력하세요.")
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', username):  # 특수문자
            raise forms.ValidationError("특수문자는 사용할 수 없습니다.")
        return username

    # 이메일 형식 제한
    ## 조건
    ## 1. 이메일 형식 (ex.orange@gmail.com)
    def clean_email(self):
        email = self.cleaned_data["email"]
        # 이메일 정규식
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            raise forms.ValidationError("이메일 형식이 올바르지 않습니다.")
        return email

    # 비밀번호 형식 제한
    ## 조건
    ## 1. 8자 이상
    ## 2. 영어 소문자, 숫자, 특수문자 반드시 포함
    def clean_password1(self):
        password = self.cleaned_data["password1"]
        if len(password) < 8:
            raise forms.ValidationError("8자 이상 입력하세요.")
        if not (
            re.search(r"[a-z]", password)
            and re.search(r"[0-9]", password)
            and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        ):
            raise forms.ValidationError("비밀번호 형식을 다시 확인해주세요.")
        return password

    # 비밀번호 확인
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return password2

    # 나이 형식 제한
    ## 조건
    ## 1. 만 나이 기준 8세 ~ 120세
    def clean_birthday(self):
        birthday = self.cleaned_data["birthday"]

        temp_user = User(birthday=birthday)
        real_age = temp_user.calculate_age()

        if real_age < 8:
            raise forms.ValidationError("만 8세부터 사용 가능한 서비스입니다.")
        if real_age > 120:
            raise forms.ValidationError("생년월일을 다시 확인해주세요.")
        return birthday


# 회원 정보 수정 폼
class EditInformationForm(UserChangeForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "현재 비밀번호"}),
        label="현재 비밀번호",
        required=True,
    )

    GENDER_CHOICE = [("남성", "남성"), ("여성", "여성")]
    gender = forms.ChoiceField(choices=GENDER_CHOICE, widget=forms.Select, label="성별")

    class Meta:
        model = User
        fields = [
            "name",
            "username",
            "email",
            "birthday",
            "gender",
        ]

        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
            "email": forms.TextInput(
                attrs={"readonly": "readonly", "class": "bg-gray-200"}
            ),
            "username": forms.TextInput(
                attrs={"readonly": "readonly", "class": "bg-gray-200"}
            ),
        }

    # 이름 형식 제한
    ## 조건
    ## 1. 2자 이상
    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 2:
            raise forms.ValidationError("2자 이상 입력하세요.")
        return name

    # 닉네임 형식 제한
    ## 조건
    ## 1. 5자 이상
    ## 2. 특수문자 사용 불가능
    def clean_username(self):
        username = self.cleaned_data["username"]
        if len(username) < 5:
            raise forms.ValidationError("5자 이상 입력하세요.")
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', username):  # 특수문자
            raise forms.ValidationError("특수문자는 사용할 수 없습니다.")
        return username

    # 이메일 형식 제한
    ## 조건
    ## 1. 이메일 형식 (ex.orange@gmail.com)
    def clean_email(self):
        email = self.cleaned_data["email"]
        # 이메일 정규식
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            raise forms.ValidationError("이메일 형식이 올바르지 않습니다.")
        return email

    # 나이 형식 제한
    ## 조건
    ## 1. 만 나이 기준 8세 ~ 120세
    def clean_birthday(self):
        birthday = self.cleaned_data["birthday"]

        temp_user = User(birthday=birthday)
        real_age = temp_user.calculate_age()

        if real_age < 8:
            raise forms.ValidationError("만 8세부터 사용 가능한 서비스입니다.")
        if real_age > 120:
            raise forms.ValidationError("생년월일을 다시 확인해주세요.")
        return birthday
