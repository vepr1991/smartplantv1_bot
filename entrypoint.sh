#!/bin/sh

if [ -z "$FIREBASE_KEY_JSON" ]; then
  echo "❌ Ошибка: переменная FIREBASE_KEY_JSON не задана!"
  exit 1
fi

echo "▶ Сохраняем ключ в firebase-key.json"
echo "$FIREBASE_KEY_JSON" > firebase-key.json

echo "▶ Проверка содержимого:"
ls -l firebase-key.json
head -n 5 firebase-key.json || echo "⚠️ Файл пуст!"

exec python bot.py
