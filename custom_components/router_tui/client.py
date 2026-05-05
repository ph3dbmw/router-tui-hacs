import asyncio
import hashlib
import random
import json
import urllib.parse
import datetime
import logging
from typing import Optional, Dict, Any, Union
from passlib.hash import sha512_crypt

_LOGGER = logging.getLogger(__name__)

class RouterClient:
    def __init__(self, base_url: str = "http://192.168.1.1", username: str = "", password: str = ""):
        import httpx
        self.base_url = base_url
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(
            timeout=15.0, 
            follow_redirects=True,
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        self.is_logged_in = False
        self.csrf_token = None

    def _log_request(self, method: str, url: str, payload: Any = None, status: int = None):
        """Append API interaction to the debug log."""
        _LOGGER.debug(f"{method} {url} | Payload: {payload} | Status: {status}")

    async def login(self, username: str = None, password: str = None) -> bool:
        """
        Attempts to authenticate with the router using the two-step SHA512-crypt handshake.
        """
        u = username or self.username
        p = password or self.password
        
        # Step 1: Request login parameters (salt and nonce)
        url_params = f"{self.base_url}/api/v1/login-params"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            # The router expects form-encoded data
            response = await self.client.post(
                url_params, 
                content=f"login={u}", 
                headers=headers
            )
            
            # 204 No Content is a success indicator for this API
            if response.status_code not in (200, 204):
                return False
            
            # Extract salt and nonce from cookies
            salt = self.client.cookies.get("salt")
            nonce = self.client.cookies.get("nonce")
            
            if not salt or not nonce:
                return False
            
            # Step 2: Calculate the challenge response
            
            # A. SHA512-crypt the password with the salt ($6$)
            crypt_result = sha512_crypt.using(salt=salt, rounds=5000).hash(p)
            
            # B. Skip the "$6$" prefix as per JS substring(3)
            crypt_trimmed = crypt_result[3:] 
            
            # C. HA1 = SHA512(username + ":" + nonce + ":" + crypt_trimmed)
            ha1_input = f"{u}:{nonce}:{crypt_trimmed}"
            ha1 = hashlib.sha512(ha1_input.encode("utf-8")).hexdigest()
            
            # D. Generate a random 19-digit cnonce (padded with zeros)
            cnonce = str(int(random.random() * 1e19)).zfill(19)
            
            # E. auth_key = SHA512(ha1 + ":0:" + cnonce)
            auth_key = hashlib.sha512(f"{ha1}:0:{cnonce}".encode("utf-8")).hexdigest()
            
            # F. Final login request
            url_login = f"{self.base_url}/api/v1/login"
            payload = f"login={u}&auth_key={auth_key}&cnonce={cnonce}"
            
            response = await self.client.post(url_login, content=payload, headers=headers)
            
            if response.status_code in (200, 204):
                self.is_logged_in = True
                # Extract CSRF token for future POST requests
                self.csrf_token = self.client.cookies.get("__Host-csrf_token")
                return True
            else:
                return False
                
        except Exception as e:
            return False

    async def get_setting(self, endpoint: str, version: str = "v1") -> Optional[Any]:
        if endpoint.startswith("/api/"):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.base_url}/api/{version}/{endpoint.lstrip('/')}"
            
        try:
            token = self.client.cookies.get("__Host-csrf_token")
            if token:
                self.csrf_token = token
                
            headers = {"X-Requested-With": "XMLHttpRequest"}
            if self.csrf_token:
                headers["X-CSRF-Token"] = self.csrf_token

            response = await self.client.get(url, headers=headers)
            self._log_request("GET", url, status=response.status_code)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {"raw": response.text}
            return None
        except Exception as e:
            return None

    async def get_home_data(self) -> Optional[Dict[str, Any]]:
        data = await self.get_setting("home", version="v2")
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    async def get_hosts(self) -> list:
        data = await self.get_setting("hosts", version="v1")
        if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return data[0].get("hosts", {}).get("list", [])
        return []

    async def close(self):
        await self.client.aclose()
