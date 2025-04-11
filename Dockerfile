# Базовый образ
FROM python:3.11-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Сохраняем секрет из переменной в файл firebase-key.json
RUN echo "$FIREBASE_KEY_JSON" > firebase-key.json


# Указываем файл ключа
ENV GOOGLE_APPLICATION_CREDENTIALS=firebase-key.json

# Запуск
CMD ["python", "bot.py"]
