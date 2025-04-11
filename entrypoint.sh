#!/bin/sh

printf "%s" "$FIREBASE_KEY_JSON" > firebase-key.json
exec python bot.py