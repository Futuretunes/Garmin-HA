"""Webhook handler for Garmin watch communication."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp.web import Request, Response, json_response

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Max entities per response to stay within Garmin's ~8-16KB limit
MAX_ENTITIES_PER_RESPONSE = 20


async def handle_webhook(
    hass: HomeAssistant,
    webhook_id: str,
    request: Request,
) -> Response:
    """Handle incoming webhook requests from the Garmin watch."""
    try:
        payload = await request.json()
    except ValueError:
        return json_response({"s": 0, "err": "invalid_json"}, status=400)

    action = payload.get("action")

    handlers = {
        "get_states": _handle_get_states,
        "call_service": _handle_call_service,
        "get_dashboard": _handle_get_dashboard,
    }

    handler = handlers.get(action)
    if handler is None:
        return json_response({"s": 0, "err": "unknown_action"}, status=400)

    try:
        return await handler(hass, payload)
    except Exception:
        _LOGGER.exception("Error handling webhook action: %s", action)
        return json_response({"s": 0, "err": "internal_error"}, status=500)


async def _handle_get_states(
    hass: HomeAssistant,
    payload: dict[str, Any],
) -> Response:
    """Return entity states, optionally filtered by domain or entity IDs."""
    domain_filter = payload.get("domain")
    entity_ids = payload.get("entity_ids")
    page = payload.get("page", 0)
    page_size = min(payload.get("page_size", MAX_ENTITIES_PER_RESPONSE), MAX_ENTITIES_PER_RESPONSE)

    all_states = hass.states.async_all(domain_filter)

    if entity_ids:
        all_states = [s for s in all_states if s.entity_id in entity_ids]

    total = len(all_states)
    start = page * page_size
    end = start + page_size
    page_states = all_states[start:end]

    entities = []
    for state in page_states:
        entities.append({
            "i": state.entity_id,
            "s": state.state,
            "n": state.attributes.get("friendly_name", state.entity_id),
        })

    return json_response({
        "s": 1,
        "e": entities,
        "t": total,
        "m": end < total,
    })


async def _handle_call_service(
    hass: HomeAssistant,
    payload: dict[str, Any],
) -> Response:
    """Call a Home Assistant service."""
    domain = payload.get("domain")
    service = payload.get("service")
    entity_id = payload.get("entity_id")
    service_data = payload.get("data", {})

    if not domain or not service:
        return json_response({"s": 0, "err": "missing_params"}, status=400)

    if entity_id:
        service_data["entity_id"] = entity_id

    await hass.services.async_call(domain, service, service_data, blocking=True)

    # Return the new state if an entity was targeted
    new_state = None
    if entity_id:
        state = hass.states.get(entity_id)
        if state:
            new_state = state.state

    return json_response({"s": 1, "ns": new_state})


async def _handle_get_dashboard(
    hass: HomeAssistant,
    payload: dict[str, Any],
) -> Response:
    """Return a compact summary of key entity states."""
    # Default domains useful for a watch dashboard
    domains = payload.get("domains", ["light", "switch", "lock", "climate", "binary_sensor"])

    items = []
    for domain in domains:
        for state in hass.states.async_all(domain):
            items.append({
                "i": state.entity_id,
                "s": state.state,
                "n": state.attributes.get("friendly_name", state.entity_id),
                "d": domain,
            })
            if len(items) >= MAX_ENTITIES_PER_RESPONSE:
                break
        if len(items) >= MAX_ENTITIES_PER_RESPONSE:
            break

    return json_response({"s": 1, "e": items})
