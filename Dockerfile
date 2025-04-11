# 🔹 Базовый образ Python
FROM python:3.11-slim

# 🔹 Рабочая директория
WORKDIR /app

# 🔹 Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 Копируем исходники
COPY . .

# 🔹 Делаем entrypoint исполняемым
RUN chmod +x entrypoint.sh

# 🔹 Запуск
CMD ["./entrypoint.sh"]
