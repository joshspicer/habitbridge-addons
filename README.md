# HabitBridge Home Assistant Addon

This addon allows Home Assistant to receive webhook data from the HabitBridge habit tracking app, making it possible to create automations based on your habit completion status.

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
   - Add the URL: `https://github.com/joshspicer/HabitBridge`
   - Click "Add"

2. Find and install the "HabitBridge" addon from the add-on store
3. Start the addon

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
>
> For local network access, you might need to use your Home Assistant's actual IP address:
> ```
> http://192.168.1.xxx:8000/webhook
> ```
> Where `192.168.1.xxx` is your Home Assistant's local IP address.

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