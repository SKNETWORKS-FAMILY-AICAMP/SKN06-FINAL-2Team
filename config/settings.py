import pymysql
from pathlib import Path
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

## 기본 설정
# 개발 모드
DEBUG = True

# secret key
SECRET_KEY = "h99x_#9)bw)beotdxobhq-g)0=@hk5kccd%!g3+!l88zt+vlz%"

# 허용되는 호스트 도메인 주소
ALLOWED_HOSTS = ["*"]

# 디렉토리 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# Apps
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "account",
    "chatbot",
    "wishlist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.NoCacheMiddleware",
]

# Root urls
ROOT_URLCONF = "config.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# wsgi
WSGI_APPLICATION = "config.wsgi.application"

# DataBases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),  # DB Name
        "USER": os.getenv("DB_USER"),  # DB User
        "PASSWORD": os.getenv("DB_PASSWORD"),  # Password
        "HOST": os.getenv("DB_HOST"),  # 생성한 데이터베이스 엔드포인트
        "PORT": "3306",
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

# password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# 언어/시간 설정
LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False

# Static
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'static'

# OpenAI API 키 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

## 추가 설정
# 브라우저 종료 시 세션 만료 (자동 로그아웃)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 로그인 해야 실행할 수 있는 View를 호출
LOGIN_URL = "/account/login"
AUTH_USER_MODEL = "account.User"  # 'account'는 해당 앱 이름

pymysql.install_as_MySQLdb()