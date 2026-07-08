#!/usr/bin/env bash
set -euo pipefail

# Safe import script to run during deploy (e.g. Render release_command)
# Behavior:
# - Requires DATABASE_URL to be set
# - Looks for USERS_BACKUP_URL (preferred) or USERS_BACKUP_PATH, or picks latest file in backups/
# - Verifies file exists and size is reasonable (<10MB)
# - Runs migrations and then imports users via management command

echo "[import_on_deploy] starting"

if [ -z "${DATABASE_URL-}" ]; then
  echo "[import_on_deploy] DATABASE_URL not set — aborting"
  exit 1
fi

mkdir -p backups

BACKUP_PATH=""

if [ -n "${USERS_BACKUP_URL-}" ]; then
  echo "[import_on_deploy] downloading backup from USERS_BACKUP_URL"
  BACKUP_PATH="backups/users_import.json"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$USERS_BACKUP_URL" -o "$BACKUP_PATH"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$BACKUP_PATH" "$USERS_BACKUP_URL"
  else
    echo "[import_on_deploy] neither curl nor wget available to download backup"
    exit 1
  fi
elif [ -n "${USERS_BACKUP_PATH-}" ]; then
  echo "[import_on_deploy] using USERS_BACKUP_PATH: $USERS_BACKUP_PATH"
  if [ -f "$USERS_BACKUP_PATH" ]; then
    BACKUP_PATH="$USERS_BACKUP_PATH"
  else
    echo "[import_on_deploy] USERS_BACKUP_PATH does not exist: $USERS_BACKUP_PATH"
    exit 1
  fi
else
  # pick latest JSON in backups/
  LATEST=$(ls -1t backups/*.json 2>/dev/null | head -n1 || true)
  if [ -n "$LATEST" ]; then
    BACKUP_PATH="$LATEST"
    echo "[import_on_deploy] found local backup: $BACKUP_PATH"
  else
    echo "[import_on_deploy] no backup found (USERS_BACKUP_URL, USERS_BACKUP_PATH, or backups/*.json) — skipping import"
    exit 0
  fi
fi

if [ ! -f "$BACKUP_PATH" ]; then
  echo "[import_on_deploy] backup file not found: $BACKUP_PATH"
  exit 1
fi

SIZE_BYTES=$(stat -c%s "$BACKUP_PATH" 2>/dev/null || stat -f%z "$BACKUP_PATH" 2>/dev/null || true)
if [ -n "$SIZE_BYTES" ] && [ "$SIZE_BYTES" -gt $((10 * 1024 * 1024)) ]; then
  echo "[import_on_deploy] backup file is too large (>10MB): $SIZE_BYTES bytes — aborting"
  exit 1
fi

echo "[import_on_deploy] running migrations"
python manage.py migrate --noinput

echo "[import_on_deploy] importing users from $BACKUP_PATH"
python manage.py import_users "$BACKUP_PATH" || {
  echo "[import_on_deploy] import_users failed" >&2
  exit 1
}

# If we downloaded the backup from a URL, remove it to avoid leaving secrets on disk
if [ -n "${USERS_BACKUP_URL-}" ] && [ -f "backups/users_import.json" ]; then
  rm -f backups/users_import.json
fi

echo "[import_on_deploy] completed successfully"
