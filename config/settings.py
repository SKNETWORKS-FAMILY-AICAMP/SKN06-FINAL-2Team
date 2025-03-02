import pymysql

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME' : 'pixary', # DB Name
        'USER' : 'pixary', # DB User
        'PASSWORD' : '!dnfl2xlavkdlxld*', # Password
        'HOST': 'pixary.cpa86cw6csn1.ap-northeast-2.rds.amazonaws.com', # 생성한 데이터베이스 엔드포인트
        'PORT': '3306', 
        'OPTIONS':{
            'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


# Internationalization
LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True