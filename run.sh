#!/bin/sh
docker compose up -d --force-recreate
echo "Waiting for Typesense to be available..."
until curl -s "$TYPESENSE_HOST/health" | grep  '{"ok":true}'; do
  sleep 2
done
sleep 5
pytest
fastapi dev main.py

