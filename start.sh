#!/bin/sh

# Run Django migrations
python manage.py migrate

# Start Django dev server in background
gunicorn attendance.wsgi:application --bind 0.0.0.0:8000 &

# Start Telegram bot
python bot/bot.py
