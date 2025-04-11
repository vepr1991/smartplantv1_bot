# Базовый образ
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Делаем скрипт исполняемым
RUN chmod +x entrypoint.sh

# Запуск через shell-скрипт
CMD ["./entrypoint.sh"]