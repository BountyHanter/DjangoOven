#!/usr/bin/env bash
set -euo pipefail

# всегда запускаемся из директории скрипта
cd "$(dirname "$0")"

# нормализуем PATH для systemd/docker/webhook
export PATH="$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

PROJECT_DIR="/var/www/DjangoOven"
HEALTH_URL="http://127.0.0.1:8000/api/v1/health/"
CHAT_ID="-1003703551676"

# ===== ВСТАВЬ СЮДА ТОКЕН =====
BOT_TOKEN="8552463815:AAE_N6N2qoXUMTVkVWB5D2bTP6Xmol69g2g"

send_tg () {
  MESSAGE=$1

  curl -v -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
       -d chat_id="${CHAT_ID}" \
       -d text="${MESSAGE}" \
       -d parse_mode="HTML" > /dev/null
}

echo "=== DEPLOY START ==="

cd $PROJECT_DIR

echo "Pulling repo..."
git pull origin main

echo "Rebuilding containers..."
docker compose build

echo "Starting containers..."
docker compose up -d

echo "Waiting for app startup..."
sleep 10

# ===== HEALTH CHECK =====

ATTEMPTS=10
SUCCESS=false

for i in $(seq 1 $ATTEMPTS); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL || true)

    if [ "$STATUS" = "200" ]; then
        SUCCESS=true
        break
    fi

    echo "Health check attempt $i failed..."
    sleep 3
done

# ===== RESULT =====

if [ "$SUCCESS" = true ]; then
    echo "Deploy success"
else
    echo "Deploy failed"

    send_tg "❌ DEPLOY FAILED

Project: DjangoOven
Stage: Health check
Server: $(hostname)
Time: $(date '+%Y-%m-%d %H:%M:%S')"

    exit 1
fi

echo "Cleaning old images..."
docker image prune -f

echo "=== DEPLOY DONE ==="

