#!/bin/bash
# 拉取最新代码
# git pull origin main

# 构建并启动容器
docker-compose down
docker-compose up -d --build

# 等待MySQL服务启动（最多等待30秒）
echo "等待MySQL启动..."
for _ in {1..30}; do
  if docker-compose exec -T db mysql -u root -pTianTu@DB_ROOT_PWD888 -e "SELECT 1" &> /dev/null; then
    echo "MySQL已就绪"
    break
  fi
  sleep 1
done

# 数据库迁移
docker-compose exec web python manage.py migrate --settings=epms_backend.settings.prod


# # 进入web容器，执行Django shell验证数据库连接
# docker-compose exec web bash

# # 执行Django shell验证数据库连接
# python manage.py shell --settings=epms_backend.settings.prod

# # 在shell中执行（无报错则连接成功）
# from django.db import connection
# cursor = connection.cursor()
# cursor.execute("SELECT 1")
# print(cursor.fetchone())  # 应输出(1,)

# # 赋予执行权限
# chmod +x deploy.sh

# # 执行部署（拉取最新代码、构建容器、启动服务、数据库迁移）
# ./deploy.sh
# # 注意：确保在运行此脚本前，已经正确配置了Docker和docker-compose，并且在项目根目录下运行此脚本。
# # 另外，确保你的Django项目中的settings.py文件已经正确配置了数据库连接和静态文件处理。
# # 你可能还需要根据你的具体需求调整脚本中的命令，例如添加日志记录、错误处理等。
# # 此脚本假设你已经有一个docker-compose.yml文件配置好了web服务和数据库服务。
