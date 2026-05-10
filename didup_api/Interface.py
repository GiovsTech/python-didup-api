from .Client import Client
from datetime import datetime
import json
import asyncio

class Argo():
    """
    This holds an object which deals with user requests
    """
    def __init__(self, client):
        self.client = client
        self.selected_profile = None

    async def get_dashboard(self):
        if not self.client.date:
            self.client.date = self.client.format_date(datetime(datetime.now().year, 9, 1))
        if not self.selected_profile:
            raise Exception("Profile isn't selected. Please select it using select_user() method.")
        body = {
            "dataultimoaggiornamento": self.client.date,
            "opzioni": '{"ORARIO_SCOLASTICO":true,"PAGELLINO_ONLINE":true,"VALUTAZIONI_PERIODICHE":true,"VALUTAZIONI_GIORNALIERE":true,"COMPITI_ASSEGNATI":true,"IGNORA_OPZIONE_VOTI_DOCENTE":true}'
        }
        headers = {
            "x-auth-token": self.selected_profile['token']
        }
        resp = await self.client.send_argo_request("/dashboard/dashboard", "POST", True, body=json.dumps(body), headers=headers)
        return resp.get("response", {}).get("data")

    async def get_profiles(self):
         body = {
            "lista-opzioni-notifiche": "{}",
            "lista-x-auth-token": "[]",
            "clientID": "d8MtQX5fR3yS9I7k-5OXUs:APA91bErrU-H7wGQ8yLastE_xS2JHDrVrfReRY2mnWQ9aVd-ohWYDTSLVRrKUsO2-25mBN1aduh5sPnZjFstg0Ixqiuoh5wCC38BB6NEveqWI_d6ZpM5DN3nvyVS8vDtwLS9caWeCmEK"
        }
         res = await self.client.send_argo_request("/login", "POST", True, body=json.dumps(body))
         profiles = []
         for profile in res['response'].get("data", []):
            profile_data_req = await self.client.send_argo_request("/profilo", "GET", True, headers={"x-auth-token": profile['token']})
            profile_data = profile_data_req.get("response", {}).get("data")
            profiles.append({
                    "profile": profile_data,
                    "token": profile['token']
                })
         return profiles

    async def select_user(self, name, surname):
        selected_profile = None
        profiles = await self.get_profiles()
        to_find = f"{surname.lower()} {name.lower()}"
        for p in profiles:
            if p["profile"]["alunno"]["nominativo"].lower() in to_find:
                selected_profile = p
            if not selected_profile:
                raise Exception("The profile you provided doesn't exist.")
        self.selected_profile = selected_profile
        return selected_profile

    async def get_details(self):
        if not self.selected_profile:
            raise Exception("Profile isn't selected. Please select it using select_user() method.")
        headers = {
            "x-auth-token": self.selected_profile['token']
        }
        resp = await self.client.send_argo_request("/dettaglioprofilo", "POST", True, headers=headers)
        return resp.get("response", {}).get("data")

    def update_date(self, date):
        formatted_date = self.client.format_date(date)
        body = { "dataultimoaggiornamento": formatted_date}
        req = self.client.send_argo_request("/dashboard/aggiorna_data", "POST", False, body=str(body))
        if req.get("status") == 200:
            self.client.date = formatted_date
            return True
        return False


