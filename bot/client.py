"""
Binance Futures Testnet REST API client wrapper.
Handles authentication, request signing, and HTTP communication.
"""

import hashlib
import hmac
import time
from urllib.parse import urlencode

import httpx

from .logging_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """Low-level signed REST client for Binance Futures Testnet."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = httpx.Client(
            base_url=BASE_URL,
            headers={"X-MBX-APIKEY": self.api_key},
            timeout=10.0,
        )

    # ------------------------------------------------------------------
    # Signing helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        """Append timestamp + HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None, signed: bool = False):
        params = params or {}
        if signed:
            params = self._sign(params)
        logger.debug("GET %s params=%s", path, params)
        try:
            resp = self.session.get(path, params=params)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("GET %s response=%s", path, data)
            return data
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error on GET %s: %s – %s", path, exc.response.status_code, exc.response.text)
            raise
        except httpx.RequestError as exc:
            logger.error("Network error on GET %s: %s", path, exc)
            raise

    def _post(self, path: str, params: dict | None = None, signed: bool = True):
        params = params or {}
        if signed:
            params = self._sign(params)
        logger.debug("POST %s params=%s", path, params)
        try:
            resp = self.session.post(path, data=params)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("POST %s response=%s", path, data)
            return data
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error on POST %s: %s – %s", path, exc.response.status_code, exc.response.text)
            raise
        except httpx.RequestError as exc:
            logger.error("Network error on POST %s: %s", path, exc)
            raise

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_exchange_info(self) -> dict:
        """Fetch exchange trading rules and symbol info."""
        return self._get("/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        """Fetch account information (requires signature)."""
        return self._get("/fapi/v2/account", signed=True)

    def place_order(self, **kwargs) -> dict:
        """
        Place a new futures order.

        Keyword args map 1-to-1 with Binance API params:
            symbol, side, type, quantity, price, timeInForce, etc.
        """
        return self._post("/fapi/v1/order", params=kwargs)
