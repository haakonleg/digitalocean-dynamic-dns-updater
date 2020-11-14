#!/bin/sh

if [[ -z "${DOMAIN}" ]]; then
  echo "ERROR: environment variable DOMAIN not set!"
  exit 1
fi

if [[ -z "${API_KEY}" ]]; then
  echo "ERROR: environment variable API_KEY not set!"
  exit 1
fi

if [[ -z "${SUBDOMAINS}" ]]; then
  echo "ERROR: environment variable SUBDOMAINS not set!"
  exit 1
fi

stop() {
  echo "Stopping..."
  exit 0
}
trap stop SIGTERM SIGINT

while true; do
  python3 /dyndns.py --domain "$DOMAIN" --apikey "$API_KEY" $SUBDOMAINS
  echo "Sleeping for $CHECK_INTERVAL seconds..."
  sleep $CHECK_INTERVAL
done
