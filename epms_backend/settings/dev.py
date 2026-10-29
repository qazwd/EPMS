from .base import *  # 继承公共配置


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-crwf+0+r-d1(!bad+tta1cg-evg3tn1n)!bi)meys096%qo0x&'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['', 'localhost', '127.0.0.1']  # 允许访问的域名或IP地址 [192.168.1.5]
ALLOWED_HOSTS = ['*']

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'api-dev.sqlite3', 
    }
}


# REST Framework 框架配置(DRF)，开发用

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [      # 添加权限验证, 要求用户登录才能访问, 否则返回403错误
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ]
}


# CORS配置，开发用

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://111.182.13.71:8080',
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie进行跨域请求


# 日志配置，开发用

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }


# 国际化配置，开发用

LANGUAGE_CODE = 'zh-hans'  # 简体中文
TIME_ZONE = 'Asia/Shanghai'  # 上海时区
USE_I18N = True
USE_TZ = True



# 开发时在 终端 或 cmd 使用

# 方法一：
# export DJANGO_SETTINGS_MODULE=epms_backend.settings.dev
# python manage.py runserver

# 方法二：
# python manage.py runserver --settings=epms_backend.settings.dev

# 启动后，访问 http://127.0.0.1:8000/api/static/企业项目管理系统.html 即可看到登陆页面

# 初始登陆
# 用户名：admin
# 密码：11111
