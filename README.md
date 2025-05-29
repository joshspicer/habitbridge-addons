> **Warning:** This addon is a work in progress and subject to significant changes!  Keep an eye this repo and the associated [the blog post](https://joshspicer.com/habitbridge) for updates!

# HabitBridge Add-on Repository

## Add-ons

This repository contains the following add-ons:

### HabitBridge

Process webhooks from HabitBridge habit tracking app

## Features

- Receives webhook data from the HabitBridge app
- Creates sensors for each habit showing completion status
- Provides a sensor for overall habit completion rate
- Creates a binary sensor that indicates when all habits are completed for the day
- Enables automations based on habit completion

## Installation

1. Add the repository to your Home Assistant addon store:
   - In Home Assistant, go to Settings -> Add-ons -> Add-on Store
   - Click the menu (⋮) in the top right corner and select "Repositories"
   - Add the URL: `https://github.com/joshspicer/habitbridge-addons`
   - Click "Add"

2. Find and install the "HabitBridge" addon from the add-on store
3. Start the addon

## Sensors Created


The addon creates the following entities in Home Assistant:

- `sensor.habitbridge` – **Summary sensor** with overall stats:
  - `state`: "on" if all habits are completed, "off" otherwise
  - Attributes:
    - `habits_count`: Number of habits
    - `completed_count`: Number of completed habits
    - `completion_rate`: Percentage of habits completed today
    - `all_habits_complete`: Boolean, true if all habits are complete
    - `user`: User name
    - `last_updated`: Last update timestamp
    - `app_version`: App version
- `sensor.habitbridge_[habit_name]` – For each habit, shows "completed" or "not_completed"
- `sensor.habitbridge_completion_rate` – Percentage of habits completed today
- `sensor.habitbridge_all_completed` – "on" when all habits are completed, "off" otherwise

## Example Automations


### LED Strip Example (using summary sensor)

This example turns an LED strip green when all habits are completed for the day, and red otherwise, using the new summary sensor:

```yaml
# Example automation for RGB LED strip
automation:
  - alias: "HabitBridge - Update LED Based on Habit Completion (Summary)"
    trigger:
      - platform: state
        entity_id: sensor.habitbridge
    action:
      - service: >
          {% if trigger.to_state.state == "on" %}
          light.turn_on
          {% else %}
          light.turn_on
          {% endif %}
        target:
          entity_id: light.led_strip
        data:
          {% if trigger.to_state.state == "on" %}
          rgb_color: [0, 255, 0]  # Green
          {% else %}
          rgb_color: [255, 0, 0]  # Red
          {% endif %}
```


### Daily Habit Reminder (using summary sensor)

```yaml
# Reminder if habits not completed by evening
automation:
  - alias: "HabitBridge - Evening Reminder (Summary)"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: state
        entity_id: sensor.habitbridge
        state: "off"
    action:
      - service: notify.mobile_app
        data:
          message: "Don't forget to complete your habits for today!"
```

### Testing the Webhook

You can use the included test script to send sample data to your webhook without needing the HabitBridge app:

```bash
# SSH into your Home Assistant instance or use the Terminal & SSH addon
cd /addons/habitbridge
python3 test_webhook.py http://localhost:8000/webhook
```

This will send sample habit data to your webhook endpoint and show the response, which is useful for verifying that the addon is working correctly.
