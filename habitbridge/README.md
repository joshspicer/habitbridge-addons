# HabitBridge Home Assistant Addon

This addon allows Home Assistant to receive webhook data from the HabitBridge habit tracking app, making it possible to create automations based on your habit completion status.

## Features

- Receives webhook data from the HabitBridge app
- Creates sensors for each habit showing completion status
- Provides a sensor for overall habit completion rate
- Creates a binary sensor that indicates when all habits are completed for the day
- Enables automations based on habit completion

## Installation

1. The addon should be automatically discovered once you add the repository
2. Start the addon

## Setup

### In Home Assistant

1. Start the addon and make note of your Home Assistant URL
2. The webhook endpoint will be available at:
   ```
   http://your-home-assistant:8000/webhook
   ```

### In the HabitBridge App

1. Open the HabitBridge app
2. Go to Settings
3. Enable Webhooks
4. Enter your Home Assistant webhook URL:
   ```
   http://your-home-assistant:8000/webhook
   ```

> **Note:** Make sure your phone can reach your Home Assistant instance on port 8000. If accessing Home Assistant over the internet, you may need to set up port forwarding or use a service like Nabu Casa for secure remote access.
