# 后端 Dockerfile —— 用于 Back4App Containers（免费档，免绑卡、免备案）
# 构建上下文为仓库根目录
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# 先装依赖，利用 Docker 层缓存
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝后端代码
COPY backend/app ./app

# Back4App 默认端口 80
EXPOSE 80

# lifespan 会自动建库建表 + 写入默认管理员
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]