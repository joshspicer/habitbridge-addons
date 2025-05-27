# HabitBridge Add-on Repository

## Add-ons

This repository contains the following add-ons:

### HabitBridge

![Latest Version][habitbridge-version-shield]
![Supports armhf Architecture][habitbridge-armhf-shield]
![Supports armv7 Architecture][habitbridge-armv7-shield]
![Supports aarch64 Architecture][habitbridge-aarch64-shield]
![Supports amd64 Architecture][habitbridge-amd64-shield]
![Supports i386 Architecture][habitbridge-i386-shield]

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

[habitbridge-version-shield]: https://img.shields.io/badge/version-v1.0.0-blue.svg
[habitbridge-armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[habitbridge-armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[habitbridge-aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[habitbridge-amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[habitbridge-i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

## Sensors Created

The addon creates the following entities in Home Assistant:

- `sensor.habitbridge_[habit_name]` - For each habit, shows "completed" or "not_completed"
- `sensor.habitbridge_completion_rate` - Percentage of habits completed today
- `sensor.habitbridge_all_completed` - "on" when all habits are completed, "off" otherwise

## Example Automations

### LED Strip Example

This example turns an LED strip green when all habits are completed for the day, and red otherwise.

```yaml
# Example automation for RGB LED strip
automation:
  - alias: "HabitBridge - Update LED Based on Habit Completion"
    trigger:
      - platform: state
        entity_id: sensor.habitbridge_all_completed
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

### Daily Habit Reminder

```yaml
# Reminder if habits not completed by evening
automation:
  - alias: "HabitBridge - Evening Reminder"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: state
        entity_id: sensor.habitbridge_all_completed
        state: "off"
    action:
      - service: notify.mobile_app
        data:
          message: "Don't forget to complete your habits for today!"
```

## Troubleshooting

- **Not receiving webhook data?** Make sure:
  - The addon is running
  - Your Home Assistant instance is accessible from your phone
  - The webhook URL is correct in the HabitBridge app
  - Check the addon logs for more information

### Testing the Webhook

You can use the included test script to send sample data to your webhook without needing the HabitBridge app:

```bash
# SSH into your Home Assistant instance or use the Terminal & SSH addon
cd /addons/habitbridge
python3 test_webhook.py http://localhost:8000/webhook
```

This will send sample habit data to your webhook endpoint and show the response, which is useful for verifying that the addon is working correctly.

## Support

For issues or feature requests, please file an issue on the [GitHub repository](https://github.com/joshspicer/HabitBridge/issues).
