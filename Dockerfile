# ✅ Базовый Python образ
FROM python:3.11-slim

# ✅ Устанавливаем рабочую директорию
WORKDIR /app

# ✅ Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Копируем все файлы проекта
COPY . .

# ✅ Убедимся, что скрипт запуска исполняемый
RUN chmod +x ./entrypoint.sh

# ✅ Явно задаём shell (важно для Render)
SHELL ["/bin/sh", "-c"]

# ✅ Запускаем через shell-скрипт
CMD ["./entrypoint.sh"]
