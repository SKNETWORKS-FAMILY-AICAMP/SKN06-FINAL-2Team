# Form 클래스 정의
## 등록폼, 수정폼 두 가지 정의

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,  # 사용자 등록폼
    UserChangeForm,  # 사용자 수정폼
)
from .models import User
from datetime import datetime


# 사용자 등록 폼
class UserCreationForm(UserCreationForm):
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

        # Input type을 변경
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

    # 이름이 올바르게 입력되었는지 확인 (2자 이상)
    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 2:
            raise forms.ValidationError("이름은 2글자 이상 입력하세요.")
        return name

    # 나이가 올바르게 입력되었는지 확인 (8 ~ 100세)
    def clean_birthday(self):
        birthday = self.cleaned_data["birthday"]
        this_year = datetime.now().year
        if (this_year - birthday.year < 8) or (this_year - birthday.year > 100):
            raise forms.ValidationError("나이가 범주를 벗어났습니다.")
        return birthday


# 사용자 정보 수정 폼
class CustomUserChangeForm(UserChangeForm):
    password = None  # password 변경링크 미표기

    STATE_CHOICE = [
        ("서울특별시", "서울특별시"),
        ("부산광역시", "부산광역시"),
        ("대구광역시", "대구광역시"),
        ("인천광역시", "인천광역시"),
        ("광주광역시", "광주광역시"),
        ("대전광역시", "대전광역시"),
        ("울산광역시", "울산광역시"),
        ("세종특별자치시", "세종특별자치시"),
        ("경기도", "경기도"),
        ("강원도", "강원도"),
        ("충청북도", "충청북도"),
        ("충청남도", "충청남도"),
        ("전라북도", "전라북도"),
        ("전라남도", "전라남도"),
        ("경상북도", "경상북도"),
        ("경상남도", "경상남도"),
    ]

    state = forms.ChoiceField(choices=STATE_CHOICE, widget=forms.Select, label="지역")

    GENDER_CHOICE = [("남성", "남성"), ("여성", "여성")]

    gender = forms.ChoiceField(choices=GENDER_CHOICE, widget=forms.Select, label="성별")

    class Meta:
        model = User
        fields = ["name", "gender", "state", "birthday", "profile_img"]

        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
            "profile_img": forms.FileInput(),
        }

    # 이름이 올바르게 입력되었는지 확인 (2자 이상)
    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 2:
            raise forms.ValidationError("이름은 2글자 이상 입력하세요.")
        return name

    # 나이가 올바르게 입력되었는지 확인 (8 ~ 100세)
    def clean_birthday(self):
        birthday = self.cleaned_data["birthday"]
        this_year = datetime.now().year
        if (this_year - birthday.year < 8) or (this_year - birthday.year > 100):
            raise forms.ValidationError("나이가 범주를 벗어났습니다.")
        return birthday
