#!/usr/bin/env python3
"""
Test script to simulate sending a webhook from HabitBridge app to the Home Assistant addon.
This is useful for testing without needing to use the actual app.

Usage:
  python3 test_webhook.py [url]

If no URL is provided, it will default to http://localhost:8000/webhook
"""
import json
import sys
import requests
from datetime import datetime, timedelta

# Get the webhook URL from command line argument or use default
webhook_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/webhook"

# Generate current date and a past date for completed habits
now = datetime.now()
today = now.isoformat()
yesterday = (now - timedelta(days=1)).isoformat()

# Create sample habit data similar to what HabitBridge app sends
sample_data = {
    "exportDate": today,
    "appVersion": "1.0.0",
    "userName": "TestUser",
    "habits": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Morning Run",
            "description": "30 min run every morning",
            "completions": [yesterday, today],  # Completed yesterday and today
            "frequency": "Daily",
            "unit": "Binary (Yes/No)",
            "targetValue": 1.0,
            "progressData": {}
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Meditation",
            "description": "15 min meditation",
            "completions": [today],  # Completed today
            "frequency": "Daily",
            "unit": "Binary (Yes/No)",
            "targetValue": 1.0,
            "progressData": {}
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "Read Book",
            "description": "Read for at least 30 minutes",
            "completions": [yesterday],  # Not completed today
            "frequency": "Daily",
            "unit": "Duration",
            "targetValue": 30.0,
            "progressData": {}
        }
    ]
}

print(f"Sending test webhook to {webhook_url}")
print(f"Sample data: {json.dumps(sample_data, indent=2)}")

try:
    response = requests.post(webhook_url, json=sample_data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")