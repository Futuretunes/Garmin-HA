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
- `__init__.py` — Entry setup: authenticates via stored tokens (`client.login(token_data)`), creates coordinator, registers webhook. Raises `ConfigEntryAuthFailed` on auth/429 errors to trigger HA reauth flow
- `coordinator.py` — `GarminHACoordinator` fetches 10 data sources from Garmin Connect (daily summary, heart rate, body battery, stress, sleep, SpO2, respiration, training readiness, HRV, last activity). Supports dot-separated nested key resolution for values like `sleepScores.overall.value`
- `sensor.py` — Creates `CoordinatorEntity`-based sensors. All sensor definitions live in `const.py` as `GarminSensorEntityDescription` tuples grouped by data source
- `config_flow.py` — Multi-strategy login flow with MFA support. Stores token data (not raw passwords) in config entries. Login order: (1) Widget SSO, (2) Standard garminconnect. Stops immediately on 429 to avoid deepening rate limits
- `widget_login.py` — Widget-based SSO login that bypasses clientId-based rate limiting. Uses `curl_cffi` with Chrome TLS impersonation to pass Cloudflare. Extracts hidden form fields, submits credentials, exchanges CAS service ticket for DI OAuth tokens
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

## garminconnect Library (v0.3.1) Gotchas

- The `Garmin` class exposes its inner client as `client.client` (NOT `client.garth`) — use `client.client.dumps()` / `client.client.loads()` for token serialization
- Token format is JSON with `di_token`, `di_refresh_token`, `di_client_id` fields
- For login with stored tokens, pass token data as the `tokenstore` parameter: `client.login(token_data)`. Data >512 chars is treated as token JSON; shorter strings are treated as file paths
- MFA flow: create `Garmin(email, password, return_on_mfa=True)`, call `login()`, check if return value is `(mfa_status, None)` with non-None status, then call `client.client.resume_login(None, mfa_code)` to complete
- **Error misclassification**: the library uses `"429" in str(error)` substring matching, so non-429 errors can be reported as `GarminConnectTooManyRequestsError`. Always check `err.__cause__` for the real HTTP status
- Garmin SSO is Cloudflare-protected and aggressively rate-limits (429) — the library tries 4 login strategies per attempt, each counting separately against the limit
- China servers (`is_cn=True`) return 401 for non-Chinese accounts — not a viable workaround

## Authentication Strategy (Widget SSO)

The `widget_login.py` module implements a fallback SSO login strategy:

1. `GET /sso/embed` — establish cookies (needs `service`, `gauthHost`, `embedWidget` params)
2. `GET /sso/signin` — get login form with CSRF token and all hidden fields
3. `POST /sso/signin` — submit credentials with all hidden fields + `_eventId=submit`
4. Extract service ticket from response (regex: `embed?ticket=...` or `ticket=...` in URL/body)
5. Exchange ticket for DI OAuth tokens via `diauth.garmin.com/di-oauth2-service/oauth/token`

Key details:
- Uses `curl_cffi` with `impersonate="chrome"` (required to pass Cloudflare TLS fingerprinting)
- The `service` URL in SSO params must match what's sent to the DI token exchange
- Rate limiting is by IP+email, not just clientId — if 429 on POST, stop immediately
- Cloudflare JS challenge cannot be bypassed programmatically — the widget works when IP is not flagged
- DI token exchange tries multiple client IDs: `GARMIN_CONNECT_MOBILE_ANDROID_DI_2025Q2`, `_2024Q4`, and base

## Releasing

- Distributed via HACS — requires a GitHub release (not just a tag) to download correctly
- Create releases with: `gh release create vX.Y.Z --target main --title "vX.Y.Z" --notes "..."`
- Keep `version` in `manifest.json` in sync with the release tag
- Current version: 0.2.9
