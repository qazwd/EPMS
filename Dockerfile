# ====================
# 第一阶段：构建依赖（命名为 builder）
# ====================
FROM python:3.10-slim-bullseye AS builder

# 设置国内 APT 源（加速依赖安装）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com\/debian-security/g' /etc/apt/sources.list

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 设置国内 PIP 源（加速依赖下载）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 构建 Python 依赖包（wheel）
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ====================
# 第二阶段：生产环境
# ====================
FROM python:3.10-slim-bullseye

# 设置国内 APT 源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com\/debian-security/g' /etc/apt/sources.list

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从 builder 阶段复制构建好的依赖包
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 设置国内 PIP 源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
RUN pip install --no-cache /wheels/*

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["gunicorn", "epms_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
