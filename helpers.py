import os
import sys
import json
import requests

def GenerateBearerToken(authorization_code: str) -> object:
    reqUrl = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"

    headersList = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ=" 
    }

    payload = f"grant_type=authorization_code&code={authorization_code}"

    response = requests.post(reqUrl, data=payload,  headers=headersList)

    return response.json()

def QueryProfile(accountId: str, profileId: str, bearer: str) -> object:
    reqUrl = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountId}/client/QueryProfile?profileId={profileId}"

    headersList = {
        "Authorization": f"bearer {bearer}",
        "Content-Type": "application/json" 
    }

    payload = json.dumps({})

    response = requests.post(reqUrl, data=payload,  headers=headersList)

    return response.json()

def getJsonPath(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)

    return os.path.join(os.path.dirname(__file__), filename)