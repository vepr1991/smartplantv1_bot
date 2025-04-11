#!/bin/sh

echo "$FIREBASE_KEY_JSON" > firebase-key.json
exec python bot.py