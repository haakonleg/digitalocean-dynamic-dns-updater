#!/bin/sh

stop() {
  echo "Stopping..."
  exit 0
}
trap stop SIGTERM SIGINT

while true; do
  python3 /dyndns.py --config "$CONFIG_FILE"
  echo "Sleeping for $CHECK_INTERVAL seconds..."
  sleep $CHECK_INTERVAL
done
