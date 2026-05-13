#!/bin/sh
set -eu

APP_TARGET="imdashboard:app"
BASE_ARGS="--interface wsgi --host 0.0.0.0 --port 5001 --workers ${WORKERS:-1} --blocking-threads ${THREADS:-1}"

if [ "${ENABLE_HTTPS:-False}" = "True" ]; then
  if test -e /certs/cert.pem && test -f /certs/key.pem; then
    exec granian ${BASE_ARGS} --ssl-certificate /certs/cert.pem --ssl-keyfile /certs/key.pem "$APP_TARGET"
  else
    echo "[ERROR] File /certs/cert.pem or /certs/key.pem NOT FOUND!"
    exit 1
  fi
else
  exec granian ${BASE_ARGS} "$APP_TARGET"
fi
