#!/usr/bin/env python3
"""
HabitBridge Home Assistant Addon
Receives webhooks from HabitBridge app and makes data available to Home Assistant
"""
import json
import logging
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
_LOGGER = logging.getLogger(__name__)

# Log the first 3 characters of the supervisor token for debugging
if SUPERVISOR_TOKEN:
    _LOGGER.info(f"SUPERVISOR_TOKEN starts with: {SUPERVISOR_TOKEN[:3]}")
else:
    _LOGGER.warning("SUPERVISOR_TOKEN is not set or empty!")

# Constants

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
HA_API_URL = 'http://supervisor/core/api'
WEBHOOK_PORT = 8000
ENTITY_PREFIX = 'sensor.habitbridge_'

# Log the first 3 characters of the supervisor token for debugging
if SUPERVISOR_TOKEN:
    _LOGGER.info(f"SUPERVISOR_TOKEN starts with: {SUPERVISOR_TOKEN[:3]}")
else:
    _LOGGER.warning("SUPERVISOR_TOKEN is not set or empty!")

app = Flask(__name__)

# Store the latest data
latest_data = {
    'habits': [],
    'userName': '',
    'exportDate': '',
    'appVersion': '',
    'allHabitsComplete': False
}

def update_ha_state(entity_id, state, attributes=None):
    """Update a Home Assistant entity state."""
    if attributes is None:
        attributes = {}
    
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    data = {
        'state': state,
        'attributes': attributes
    }
    
    try:
        response = requests.post(
            f"{HA_API_URL}/states/{entity_id}",
            headers=headers,
            json=data
        )
        if response.status_code not in (200, 201):
            _LOGGER.error(f"Failed to update entity {entity_id}: {response.text}")
        else:
            _LOGGER.debug(f"Updated {entity_id} to {state}")
    except Exception as e:
        _LOGGER.error(f"Error updating {entity_id}: {str(e)}")

def is_habit_completed_today(habit):
    """Check if a habit is completed today."""
    today = datetime.now().date()
    IOS_EPOCH = datetime(2001, 1, 1)
    for completion_date in habit.get('completions', []):
        dt = None
        if isinstance(completion_date, (int, float)):
            try:
                # Interpret as iOS timestamp (seconds since 2001-01-01)
                dt = IOS_EPOCH + timedelta(seconds=completion_date)
            except Exception:
                continue
        elif isinstance(completion_date, str):
            try:
                # Try parsing as ISO string
                dt = datetime.fromisoformat(completion_date)
            except Exception:
                continue
        if dt and dt.date() == today:
            return True
    return False

def process_habits_data(data):
    """Process the habit data received from webhook."""
    habits = data.get('habits', [])
    user_name = data.get('userName', 'Unknown User')
    export_date = data.get('exportDate', datetime.now().isoformat())
    app_version = data.get('appVersion', 'Unknown')
    
    # Update global data store
    global latest_data
    latest_data['habits'] = habits
    latest_data['userName'] = user_name
    latest_data['exportDate'] = export_date
    latest_data['appVersion'] = app_version
    
    # Track completion of all habits for today
    all_habits_complete = True
    completed_count = 0
    
    # Update individual habit sensors
    for habit in habits:
        habit_id = habit.get('id', 'unknown')
        habit_name = habit.get('name', 'Unknown Habit')
        habit_completed = is_habit_completed_today(habit)
        
        if habit_completed:
            completed_count += 1
        else:
            all_habits_complete = False
        
        # Create a sanitized entity ID
        safe_name = habit_name.lower().replace(' ', '_')
        entity_id = f"{ENTITY_PREFIX}{safe_name}"
        
        # Update habit state
        state = "completed" if habit_completed else "not_completed"
        attributes = {
            'friendly_name': f"HabitBridge: {habit_name}",
            'description': habit.get('description', ''),
            'frequency': habit.get('frequency', 'daily'),
            'last_updated': datetime.now().isoformat(),
            'habit_id': habit_id,
            'user': user_name
        }
        update_ha_state(entity_id, state, attributes)
    
    # Update summary sensors
    latest_data['allHabitsComplete'] = all_habits_complete
    
    # Update overall completion rate
    completion_rate = 0
    if habits:
        completion_rate = (completed_count / len(habits)) * 100
    
    update_ha_state(
        f"{ENTITY_PREFIX}completion_rate",
        round(completion_rate, 1),
        {
            'friendly_name': "HabitBridge Completion Rate",
            'unit_of_measurement': "%",
            'icon': "mdi:check-circle-outline",
            'user': user_name,
            'last_updated': datetime.now().isoformat()
        }
    )
    
    # Update all habits complete sensor
    update_ha_state(
        f"{ENTITY_PREFIX}all_completed",
        "on" if all_habits_complete else "off",
        {
            'friendly_name': "HabitBridge All Habits Completed",
            'icon': "mdi:check-all",
            'user': user_name,
            'last_updated': datetime.now().isoformat()
        }
    )

    # Update a single summary entity for HabitBridge
    update_ha_state(
        "sensor.habitbridge",
        "on" if all_habits_complete else "off",
        {
            'friendly_name': "HabitBridge Summary",
            'icon': "mdi:bridge-variant",
            'user': user_name,
            'habits_count': len(habits),
            'completed_count': completed_count,
            'completion_rate': round(completion_rate, 1),
            'all_habits_complete': all_habits_complete,
            'last_updated': datetime.now().isoformat(),
            'app_version': app_version
        }
    )
    
    _LOGGER.info(f"Processed habits data: {len(habits)} habits, {completed_count} completed")
    return all_habits_complete, completion_rate

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from HabitBridge app."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        _LOGGER.info(f"Received webhook data for user: {data.get('userName', 'Unknown')}")
        
        all_complete, completion_rate = process_habits_data(data)
        
        return jsonify({
            "status": "success",
            "message": "Data processed successfully",
            "all_complete": all_complete,
            "completion_rate": completion_rate
        })
        
    except Exception as e:
        _LOGGER.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Return the current status of habits."""
    return jsonify({
        "status": "online",
        "habits_count": len(latest_data['habits']),
        "user": latest_data['userName'],
        "all_complete": latest_data['allHabitsComplete'],
        "last_updated": latest_data['exportDate']
    })

if __name__ == "__main__":
    _LOGGER.info(f"Starting HabitBridge webhook server on port {WEBHOOK_PORT}")
    
    # Add a root route that provides a simple UI
    @app.route('/', methods=['GET'])
    def index():
        return """
        <html>
            <head>
                <title>HabitBridge Webhook Server</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .container { background-color: #f5f5f5; border-radius: 10px; padding: 20px; }
                    pre { background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }
                    .success { color: green; }
                    .endpoint { font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>HabitBridge Webhook Server</h1>
                    <p class="success">✅ Server is running!</p>
                    
                    <h2>Webhook Endpoint:</h2>
                    <p class="endpoint">http://[your-server]:{WEBHOOK_PORT}/webhook</p>
                    
                    <h2>Available Routes:</h2>
                    <ul>
                        <li><code>/webhook</code> - POST endpoint for HabitBridge app to send data</li>
                        <li><code>/status</code> - GET endpoint to check server status</li>
                    </ul>
                    
                    <h2>Setup Instructions:</h2>
                    <p>In the HabitBridge app, set your webhook URL to:</p>
                    <pre>http://[your-home-assistant-ip]:{WEBHOOK_PORT}/webhook</pre>
                    
                    <p>For more information, see the <a href="https://github.com/joshspicer/HabitBridge-addons">README</a></p>
                </div>
            </body>
        </html>
        """
    
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)