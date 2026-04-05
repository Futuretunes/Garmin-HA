# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Garmin HA is a two-part system that connects Garmin watches to Home Assistant:

1. **Home Assistant custom integration** (`custom_components/garmin_ha/`) — A HACS-compatible integration that polls Garmin Connect for health/fitness data and exposes a webhook API for the watch app.
2. **Garmin Connect IQ watch app** (`connectiq/garmin-ha-app/`) — A Monkey C app for Garmin Epix 2 watches that communicates with Home Assistant via the webhook to browse and control entities.

## Architecture

### Data flow

```
Garmin Connect API  -->  HA Integration (coordinator polls every 5min)  -->  HA Sensor entities
Garmin Watch App  <--webhook HTTP-->  HA Integration (webhook.py)  <-->  HA entity states/services
```

### HA Integration (`custom_components/garmin_ha/`)

- **Python, uses `garminconnect` library (v0.3.1)** and Home Assistant's `DataUpdateCoordinator` pattern
- `__init__.py` — Entry setup: authenticates via Garth tokens, creates coordinator, registers webhook
- `coordinator.py` — `GarminHACoordinator` fetches 10 data sources from Garmin Connect (daily summary, heart rate, body battery, stress, sleep, SpO2, respiration, training readiness, HRV, last activity). Supports dot-separated nested key resolution for values like `sleepScores.overall.value`
- `sensor.py` — Creates `CoordinatorEntity`-based sensors. All sensor definitions live in `const.py` as `GarminSensorEntityDescription` tuples grouped by data source
- `config_flow.py` — Credentials-based setup storing Garth token data (not raw passwords) in config entries
- `webhook.py` — Handles three actions from the watch: `get_states` (paginated entity listing), `call_service` (toggle/control), `get_dashboard` (compact multi-domain summary). Responses use abbreviated keys (`i`, `s`, `n`, `d`) to stay within Garmin's ~8-16KB BLE transfer limit

### Watch App (`connectiq/garmin-ha-app/`)

- **Monkey C, Connect IQ SDK 3.4.0+**, targets Epix 2 family devices
- `GarminHAApp.mc` — Entry point; checks settings, shows MainMenuView or ErrorView
- `Settings.mc` — Reads app properties (HA URL, webhook ID, API key, refresh interval) configured via Garmin Connect mobile app
- `HAClient.mc` — HTTP client module; POSTs JSON to the webhook URL. Tracks `_requestInFlight` to avoid BLE queue overflow (single request at a time)
- `MainMenuView.mc` — Domain category menu (Lights, Switches, Climate, Locks, Sensors, Scenes, Scripts)
- `EntityListView.mc` — Lists entities within a domain; toggleable entities toggle on select, non-toggleable push to detail view
- `EntityDetailView.mc` — Shows entity name/state/ID with toggle action for supported domains
- `Constants.mc` — Domain strings, AMOLED-optimized color palette, toggle logic per domain type
- `LoadingView.mc` / `ErrorView.mc` — UI feedback views

## Build & Development

### HA Integration

- Requires Home Assistant 2024.1.0+
- Install via HACS or copy `custom_components/garmin_ha/` to HA's `custom_components/` directory
- No test suite currently exists
- Translations: `strings.json` and `translations/en.json` must stay in sync

### Connect IQ Watch App

- Requires Garmin Connect IQ SDK (min 3.4.0)
- Build: `monkeyc -f connectiq/garmin-ha-app/monkey.jungle -o bin/garmin-ha.prg -d epix2`
- The app has no barrel dependencies
- Settings are configured by end users through the Garmin Connect mobile app (defined in `resources/settings/`)

## Key Conventions

- Webhook responses use single-character keys (`s`=status/state, `e`=entities, `i`=entity_id, `n`=name, `d`=domain, `t`=total, `m`=more pages) to minimize payload size for BLE transfer
- Sensor descriptions in `const.py` use a `source` field that maps to coordinator data dict keys and a `value_key` that maps to the Garmin Connect API response fields (camelCase)
- The watch app uses `_requestInFlight` guard pattern — only one HTTP request at a time to prevent Garmin BLE queue errors
