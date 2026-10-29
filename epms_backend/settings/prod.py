# 生产环境配置文件（未完善）

import os

# from epms_backend.epms_backend.settings import REST_FRAMEWORK
from .base import *
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件中的环境变量


# 生产环境特有配置（安全优先）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')  # 从环境变量获取密钥（禁止硬编码）
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True' # 从环境变量获取调试模式
# ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']  # 仅允许指定域名访问
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(", ")


# 生产数据库（MySQL）

# 生产数据库（支持多种数据库）
import os
db_engine = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}
# 根据数据库类型添加特定选项
if 'mysql' in db_engine:
    DATABASES['default']['OPTIONS'] = {
        'charset': 'utf8mb4',  # 支持中文及特殊字符
        'sql_mode': 'STRICT_TRANS_TABLES',  # 严格模式，避免数据不一致
    }

# REST Framework（生产严格权限）

REST_FRAMEWORK.update({
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # 仅允许登录用户访问
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 可选：添加JWT认证
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
})


# CORS（生产环境）

CORS_ALLOW_ALL_ORIGINS = False  # 禁止所有来源

CORS_ALLOW_ORIGINS = [
    # 'https://your-domain.com',  # 仅允许前端域名
    # 'https://www.your-domain.com',

    'http://localhost:8000',
    'http://127.0.0.1:8000',

    'http://192.168.5.8:8000',
    'http://192.168.5.19:8000',

    'http://111.182.13.71:8000',
]

CORS_ALLOW_CREDENTIALS = True  # 如需跨域携带cookie则开启


# 静态文件（生产收集目录）

STATIC_ROOT = BASE_DIR / 'staticfiles'  # 执行collectstatic时的目标目录


# 生产安全增强

SECURE_SSL_REDIRECT = False  # 强制HTTPS
SESSION_COOKIE_SECURE = True  # Cookie仅通过HTTPS传输
CSRF_COOKIE_SECURE = True  # CSRF Cookie仅通过HTTPS传输
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'  # 禁止iframe嵌入


# 生产日志（输出到文件，仅记录警告及以上）

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',  # 日志文件路径
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}


# 使用说明：
# 1. 确保已安装MySQL数据库，且数据库服务已启动
# 2. 确保已创建名为epms的数据库（或根据.env文件中的DB_NAME修改）
# 3. 确保已配置环境变量DJANGO_SETTINGS_MODULE=epms_backend.settings.prod
# 4. 执行python manage.py migrate创建数据库表
# 5. 执行python manage.py collectstatic收集静态文件
# 6. 启动应用（如使用Gunicorn：gunicorn epms_backend.wsgi:application --settings=epms_backend.settings.prod）


# 终端执行（或在部署脚本中配置）
# export DJANGO_SETTINGS_MODULE=epms_backend.settings.prod
# 或在启动命令中指定：
# gunicorn epms_backend.wsgi:application --settings=epms_backend.settings.prod
# 注意：生产环境请使用Gunicorn或uWSGI等WSGI服务器，不要使用Django自带的开发服务器
