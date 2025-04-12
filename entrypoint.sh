#!/bin/sh

if [ -z "$FIREBASE_KEY_JSON" ]; then
  echo "❌ Переменная FIREBASE_KEY_JSON не задана!"
  exit 1
fi

echo "$FIREBASE_KEY_JSON" > firebase-key.json
echo "▶ Содержимое переменной:"
echo "$FIREBASE_KEY_JSON"

exec python bot.py
