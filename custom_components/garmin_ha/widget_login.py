"""Widget-based SSO login for Garmin Connect.

Bypasses clientId-based rate limiting by using the HTML form-based SSO
embed widget endpoint, which does not send a clientId parameter.

Uses curl_cffi to impersonate Chrome's TLS fingerprint so Cloudflare
does not block the requests.

Based on the approach described in:
https://github.com/cyberjunky/python-garminconnect/issues/344
"""

from __future__ import annotations

import json
import logging
import re
from base64 import b64encode

from curl_cffi import requests as cffi_requests

_LOGGER = logging.getLogger(__name__)

SSO_BASE = "https://sso.garmin.com/sso"
SSO_EMBED_URL = f"{SSO_BASE}/embed"
SSO_SIGNIN_URL = f"{SSO_BASE}/signin"
SSO_MFA_URL = f"{SSO_BASE}/verifyMFA/loginEnterMfaCode"

SSO_EMBED_PARAMS = {
    "id": "gauth-widget",
    "embedWidget": "true",
    "gauthHost": SSO_BASE,
}

DI_TOKEN_URL = "https://diauth.garmin.com/di-oauth2-service/oauth/token"
DI_GRANT_TYPE = (
    "https://connectapi.garmin.com/di-oauth2-service/oauth/grant/service_ticket"
)
DI_CLIENT_IDS = (
    "GARMIN_CONNECT_MOBILE_ANDROID_DI_2025Q2",
    "GARMIN_CONNECT_MOBILE_ANDROID_DI_2024Q4",
    "GARMIN_CONNECT_MOBILE_ANDROID_DI",
)
DI_SERVICE_URLS = (
    "https://connect.garmin.com/modern/",
    "https://connect.garmin.com/app",
)

_CSRF_RE = re.compile(r'name="_csrf"\s+value="([^"]+)"')
_TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)
_TICKET_RE = re.compile(r"embed\?ticket=([^\"&\s]+)")
_TICKET_FALLBACK_RE = re.compile(r"ticket=([A-Za-z0-9_-]+)")


class WidgetLoginError(Exception):
    """Widget SSO login failed."""


class WidgetAuth:
    """Handles authentication via the SSO embed widget form."""

    def __init__(self) -> None:
        self._session = cffi_requests.Session(
            impersonate="chrome", timeout=30
        )
        self._last_html: str = ""

    def login(self, email: str, password: str) -> str | None:
        """Authenticate via SSO widget.

        Returns token_data JSON on success, or None if MFA is required
        (call submit_mfa next).
        """
        _LOGGER.warning("Widget SSO: starting login attempt")

        # Step 1: establish SSO cookies
        r = self._session.get(SSO_EMBED_URL, params=SSO_EMBED_PARAMS)
        _LOGGER.warning("Widget SSO: embed response status=%s", r.status_code)
        if r.status_code == 429:
            raise WidgetLoginError(
                f"SSO embed endpoint returned 429: {r.text[:200]}"
            )
        r.raise_for_status()

        # Step 2: get CSRF token from signin form
        r = self._session.get(
            SSO_SIGNIN_URL,
            params=SSO_EMBED_PARAMS,
            headers={"Referer": SSO_EMBED_URL},
        )
        _LOGGER.warning("Widget SSO: signin page status=%s", r.status_code)
        r.raise_for_status()

        csrf = self._extract_csrf(r.text)
        if not csrf:
            _LOGGER.warning(
                "Widget SSO: no CSRF token found, body[:500]=%s",
                r.text[:500],
            )
            raise WidgetLoginError("Could not find CSRF token in SSO form")

        # Step 3: POST credentials
        r = self._session.post(
            SSO_SIGNIN_URL,
            params=SSO_EMBED_PARAMS,
            data={
                "username": email,
                "password": password,
                "embed": "true",
                "_csrf": csrf,
            },
            headers={"Referer": SSO_SIGNIN_URL},
        )
        _LOGGER.warning("Widget SSO: login POST status=%s", r.status_code)
        r.raise_for_status()
        self._last_html = r.text

        return self._handle_response(r)

    def submit_mfa(self, mfa_code: str) -> str:
        """Submit MFA code and complete authentication.

        Returns token_data JSON.
        """
        csrf = self._extract_csrf(self._last_html)

        r = self._session.post(
            SSO_MFA_URL,
            data={
                "mfa-code": mfa_code,
                "embed": "true",
                "_csrf": csrf or "",
                "_eventId": "submit",
            },
            headers={"Referer": SSO_SIGNIN_URL},
        )
        r.raise_for_status()
        self._last_html = r.text

        result = self._handle_response(r)
        if result is None:
            raise WidgetLoginError("MFA verification failed")
        return result

    def _handle_response(self, response: cffi_requests.Response) -> str | None:
        """Process SSO response — extract ticket or detect MFA."""
        title = self._extract_title(response.text)

        # Detect MFA prompt
        if title and "mfa" in title.lower():
            _LOGGER.debug("Widget SSO: MFA required")
            return None

        # Detect auth failures
        if title:
            fail_words = ("locked", "invalid", "incorrect", "error", "failed")
            if any(w in title.lower() for w in fail_words):
                raise WidgetLoginError(
                    f"Authentication failed (SSO page title: {title!r})"
                )

        # Extract service ticket
        ticket = self._extract_ticket(response)
        if not ticket:
            _LOGGER.warning(
                "Widget SSO: no ticket found. Title=%r, URL=%s, body[:500]=%s",
                title, response.url, response.text[:500],
            )
            raise WidgetLoginError(
                "Could not extract service ticket from SSO response"
            )

        _LOGGER.warning("Widget SSO: got service ticket, exchanging for tokens")
        return self._exchange_ticket(ticket)

    def _extract_csrf(self, html: str) -> str | None:
        m = _CSRF_RE.search(html)
        return m.group(1) if m else None

    def _extract_title(self, html: str) -> str | None:
        m = _TITLE_RE.search(html)
        return m.group(1).strip() if m else None

    def _extract_ticket(self, response: cffi_requests.Response) -> str | None:
        # Primary: ticket in embed response body (embed?ticket=...)
        m = _TICKET_RE.search(response.text)
        if m:
            return m.group(1)

        # Fallback: ticket in final URL after redirects
        m = _TICKET_FALLBACK_RE.search(response.url)
        if m:
            return m.group(1)

        # Fallback: ticket anywhere in response body
        m = _TICKET_FALLBACK_RE.search(response.text)
        if m:
            return m.group(1)

        return None

    def _exchange_ticket(self, ticket: str) -> str:
        """Exchange CAS service ticket for DI OAuth tokens."""
        last_error = None

        for service_url in DI_SERVICE_URLS:
            for client_id in DI_CLIENT_IDS:
                basic = b64encode(f"{client_id}:".encode()).decode()
                try:
                    r = self._session.post(
                        DI_TOKEN_URL,
                        headers={
                            "Authorization": f"Basic {basic}",
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json",
                        },
                        data={
                            "client_id": client_id,
                            "service_ticket": ticket,
                            "grant_type": DI_GRANT_TYPE,
                            "service_url": service_url,
                        },
                    )
                except Exception as exc:
                    _LOGGER.warning("DI exchange request failed: %s", exc)
                    last_error = exc
                    continue

                if r.status_code == 429:
                    _LOGGER.warning(
                        "DI exchange rate limited for %s / %s",
                        client_id, service_url,
                    )
                    last_error = WidgetLoginError("DI token exchange rate limited")
                    continue

                if not r.ok:
                    _LOGGER.warning(
                        "DI exchange failed for %s / %s: %s %s",
                        client_id, service_url, r.status_code, r.text[:200],
                    )
                    continue

                try:
                    data = r.json()
                    token_data = json.dumps({
                        "di_token": data["access_token"],
                        "di_refresh_token": data.get("refresh_token"),
                        "di_client_id": client_id,
                    })
                    _LOGGER.info(
                        "Widget SSO login successful (client=%s, svc=%s)",
                        client_id, service_url,
                    )
                    return token_data
                except (KeyError, ValueError) as exc:
                    _LOGGER.warning(
                        "DI token parse failed for %s: %s", client_id, exc
                    )
                    last_error = exc
                    continue

        raise WidgetLoginError(
            f"DI token exchange failed for all client/service combinations: "
            f"{last_error}"
        )
