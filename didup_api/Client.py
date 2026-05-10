from .lib.getToken import getToken
from .lib.argo_requests import sendArgoRequest
from .lib.Constants import scopes, ClientId, redirectUri, baseApiURL
import os
import json
from datetime import datetime, timedelta
import requests

class Client():
    """
    Just an object designed to hold generical functions needed by Argo Interface
    """
    def __init__(self, schoolCode, username, password, configPath, save_login=True):
        self.account_credentials = {
            "schoolCode": schoolCode,
            "username": username,
            "password": password
        }
        self.configPath = configPath
        self.saveLogin = save_login
        self.date = "" ## The date (+ time) of the latest request to Argo API
        self.token =  { "access_token": "", "expires_at": "undefined", "id_token": "", "refresh_token": "", "scope": "openid offline profile user.roles argo", "token_type": "bearer" }

    def format_date(self, data):
        return data.strftime("%Y-%m-%d %H:%M:%S")

    def refresh_token(self):
        """
        This refreshes the token in case it has expired.
        """
        url = "https://auth.portaleargo.it/oauth2/token"
        payload = {
            "refresh_token": self.token.get("refresh_token"),
            "grant_type": "refresh_token",
            "scope": scopes,
            "client_id": ClientId,
            "redirect_uri": redirectUri
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 401:
            return None
        data = response.json()
        expires_in = data.pop("expires_in", None)
        if expires_in is not None:
            data["expires_at"] = datetime.now() + timedelta(seconds=expires_in)
        return data

    async def send_argo_request(self, path, method, parse_body=True, body=None, headers=None):
        """
        This method is a wrapper for sendArgoRequest function
        """
        req = await sendArgoRequest(self, path, method, body, headers, parse_body)
        return req

    async def login(self):
        """
        It saves login token to a file user has provided
        """
        self.token = await getToken(self.account_credentials)
        if not self.saveLogin:
            return
        if not os.path.exists(self.configPath):
            os.makedirs(self.configPath)
            self._write_token_file()
        else:
            token_file = self._get_token_file_path()
            if os.path.exists(token_file):
                with open(token_file, 'r', encoding='utf-8') as f:
                    self.token = json.load(f)
                if self.token.get("expires_at") and self._is_token_expired(self.token["expires_at"]):
                    new_token = self.refresh_token()
                    if not new_token:
                        self.token = await getToken(self.account_credentials)
                        if not await self.attempt_access_token():
                            self.token = await getToken(self.account_credentials)
                            self._write_token_file()
                        else:
                            self._write_token_file()

    async def get_profile(self):
        req = await self.send_argo_request("/profilo", "GET", True)
        return req.get('response')

    async def attempt_access_token(self):
        """
        It checks if the provided token is valid to log in
        """
        req = await self.send_argo_request(
            "/login", "POST", False,
            json.dumps({
                "lista-opzioni-notifiche": "{}",
                "lista-x-auth-token": "[]",
                "clientID": "d8MtQX5fR3yS9I7k-5OXUs:APA91bErrU-H7wGQ8yLastE_xS2JHDrVrfReRY2mnWQ9aVd-ohWYDTSLVRrKUsO2-25mBN1aduh5sPnZjFstg0Ixqiuoh5wCC38BB6NEveqWI_d6ZpM5DN3nvyVS8vDtwLS9caWeCmEK"
            })
        )
        if req.get('status') == 401:
            return False
        return True

    def _get_token_file_path(self):
        return os.path.join(
            self.configPath,
            f"{self.account_credentials['schoolCode']}_{self.account_credentials['username']}.json"
        )

    def _write_token_file(self):
        token_file = self._get_token_file_path()
        with open(token_file, 'w', encoding='utf8') as f:
            json.dump(self.token, f)

    def _is_token_expired(self, expires_at):
        try:
            expiry = datetime.fromisoformat(expires_at)
            return expiry.timestamp() < datetime.now().timestamp()
        except Exception:
            return True
