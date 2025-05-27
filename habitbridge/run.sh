#!/usr/bin/with-contenv bashio

CONFIG_PATH=/data/options.json
LOG_LEVEL=$(bashio::config 'log_level')

# Start the Flask server
exec python3 /app.py