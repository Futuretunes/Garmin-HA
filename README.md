# Garmin HA

A two-part system that connects Garmin watches to Home Assistant:

- **Home Assistant custom integration** -- Polls Garmin Connect for health/fitness data and exposes a webhook API for the watch app.
- **Garmin Connect IQ watch app** -- A Monkey C app for Garmin Epix 2 watches that communicates with Home Assistant to browse and control entities.

## Features

### Health & Fitness Sensors

The integration creates HA sensors from 10 Garmin Connect data sources:

| Category | Sensors |
|---|---|
| Daily Summary | Steps, distance, calories, floors, intensity minutes |
| Heart Rate | Resting, max, min |
| Body Battery | Current, highest, lowest, charged, drained |
| Stress | Overall level, rest/low/medium/high durations, qualifier |
| Sleep | Score, duration, deep/light/REM/awake breakdown |
| SpO2 | Latest, lowest, average |
| Respiration | Waking avg, sleeping avg, highest, lowest |
| Training Readiness | Score |
| HRV | Weekly average |
| Last Activity | Name, type, distance, duration, calories |

Data is polled every 5 minutes via the Garmin Connect API.

### Watch App

Control your Home Assistant from your wrist:

- Browse entities by domain (Lights, Switches, Climate, Locks, Sensors, Scenes, Scripts)
- Toggle lights, switches, locks, and scenes
- View entity states and details
- Paginated entity lists for large setups
- AMOLED-optimized color palette

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Garmin HA" and install
3. Restart Home Assistant
4. Go to **Settings > Devices & Services > Add Integration** and search for "Garmin HA"
5. Enter your Garmin Connect credentials (MFA supported)

### Manual

Copy `custom_components/garmin_ha/` into your Home Assistant `custom_components/` directory and restart.

### Watch App

Requires the Garmin Connect IQ SDK (3.4.0+).

```
monkeyc -f connectiq/garmin-ha-app/monkey.jungle -o bin/garmin-ha.prg -d epix2
```

Configure the webhook URL, webhook ID, and API key through the Garmin Connect mobile app settings.

## Requirements

- Home Assistant 2024.1.0+
- A Garmin Connect account
- For the watch app: Garmin Epix 2 family device

## How It Works

```
Garmin Connect API  -->  HA Integration (polls every 5 min)  -->  HA Sensor entities
Garmin Watch App  <--webhook-->  HA Integration  <-->  HA entity states/services
```

The integration authenticates to Garmin Connect using stored OAuth tokens. If Garmin's SSO rate-limits the standard login (a known issue with the `garminconnect` library), the integration automatically falls back to a widget-based SSO strategy that bypasses the rate limiting.

Watch communication uses abbreviated JSON keys (`i`, `s`, `n`, `d`) to stay within Garmin's ~8-16KB BLE transfer limit.

## Troubleshooting

### "Too many requests" or login failures

Garmin aggressively rate-limits SSO logins. The integration includes an automatic fallback (widget SSO) that bypasses this. If you still see errors, check the HA logs for lines containing `Widget SSO` to see detailed diagnostics.

### Reauthorization

If your tokens expire, the integration will trigger HA's reauth flow -- you'll see a notification to re-enter your Garmin credentials.

## License

MIT
