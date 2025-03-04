import os
import sys
import json
import asyncio
import threading
import zlib
import base64
import aiohttp
import requests
import webbrowser
import tkinter as tk
from tkinter import messagebox
from colored import fg
from colorama import Fore
from tkinter import font

zold = fg('green')

# setting acceptable cosmetic types
ACCEPTED_COSMETIC_TYPES = [
    "AthenaCharacter",
    "AthenaDance",
    "AthenaPickaxe",
    "AthenaBackpack",
    "AthenaGlider",
    "AthenaItemWrap",
    "AthenaLoadingScreen",
    "AthenaMusicPack",
    "AthenaSkyDiveContrail",
    "BannerToken",
    "HomebaseBannerIcon",
    "SparksSong",
    "SparksGuitar",
    "SparksBass",
    "SparksDrums",
    "SparksKeyboard",
    "SparksMicrophone",
    "SparksAura",
    "VehicleCosmetics_Body",
    "VehicleCosmetics_Skin",
    "VehicleCosmetics_Wheel",
    "VehicleCosmetics_DriftTrail",
    "VehicleCosmetics_Booster",
    "JunoBuildingProp",
    "JunoBuildingSet"
]

class User:
    AccountId = ""
    UserName = ""
    AccessToken = ""

def QueryProfile(accountId: str, profileId: str, bearer: str) -> object:
    reqUrl = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountId}/client/QueryProfile?profileId={profileId}"

    headersList = {
        "Authorization": f"bearer {bearer}",
        "Content-Type": "application/json" 
    }

    payload = json.dumps({})

    response = requests.post(reqUrl, data=payload,  headers=headersList)

    return response.json()

def CheckBundle(bundleId, data, profileItems, fnggItems) -> int:
    countOfShould = len(data['items'])
    countOfActual = 0

    for i in data['items']:
        if i.lower() in profileItems:
            countOfActual += 1

    if countOfShould == countOfActual:
        return fnggItems[bundleId.lower()]
    else:
        return None

def getJsonPath(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)

    return os.path.join(os.path.dirname(__file__), filename)

# DEVICE CODE AUTH (https://github.com/xMistt/DeviceAuthGenerator)

SWITCH_TOKEN = "OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3"

async def getAccessToken(http_session) -> str:
    async with http_session.request(
        method="POST",
        url="https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic {SWITCH_TOKEN}",
        },
        data={
            "grant_type": "client_credentials",
        },
    ) as request:
        data = await request.json()

    return data["access_token"]

async def createDeviceCode(http_session, access_token) -> tuple:
    async with http_session.request(
        method="POST",
        url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization",
        headers={
            "Authorization": f"bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    ) as request:
        data = await request.json()

    return data["verification_uri_complete"], data["device_code"]

async def waitForDeviceCodeComplete(http_session, code) -> dict:
    while True:
        async with http_session.request(
            method="POST",
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
            headers={
                "Authorization": f"basic {SWITCH_TOKEN}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "device_code", "device_code": code},
        ) as request:
            if request.status == 200:
                auth_data = await request.json()
                break
            else:
                pass

            await asyncio.sleep(3)

    return auth_data

def open_link(url):
    webbrowser.open(url, new=1)
def start_app():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def run_loop():
        loop.run_forever()

    threading.Thread(target=run_loop, daemon=True).start()

    root = tk.Tk()
    root.title("FNGG Locker")
    root.geometry("300x300")

    tk.Label(root, text="FNGG Locker", font=("Helvetica", 16)).pack(pady=10)


    async def authenticate():
        # Get all child widgets of root
        widgets = root.winfo_children()
        # Find the index of the authentication button
        for idx, widget in enumerate(widgets):
            if isinstance(widget, tk.Button) and widget["text"] == "Start Authentication":
                start_index = idx + 1
                break
        else:
            start_index = len(widgets)
        # Destroy widgets after the button
        for widget in widgets[start_index:]:
            widget.destroy()
        async with aiohttp.ClientSession() as http_session:
            access_token = await getAccessToken(http_session)
            device_url, device_code = await createDeviceCode(http_session, access_token)
            tk.Label(root, text="Please log in to your account by clicking this link:", font=("Helvetica", 12)).pack(pady=5)
            underline_font = font.Font(family="Helvetica", size=12, underline=True)
            link = tk.Label(root, text="Click here to log in", font=underline_font, fg="white", cursor="hand2")
            link.pack(pady=5)
            link.bind("<Button-1>", lambda _: open_link(device_url))
            auth_data = await waitForDeviceCodeComplete(http_session, device_code)

        User.AccountId = auth_data["account_id"]
        User.UserName = auth_data["displayName"]
        User.AccessToken = auth_data["access_token"]

        tk.Label(root, text=f"Username: {User.UserName}", font=("Helvetica", 12)).pack(pady=5)

        JSONDATA = QueryProfile(User.AccountId, "athena", User.AccessToken)
        JSONDATA_CC = QueryProfile(User.AccountId, "common_core", User.AccessToken)

        packsDataReq = requests.get("https://api.fecooo.hu/fngg/offers")
        if packsDataReq.status_code == 200:
            PACKSDATA = packsDataReq.json()
        else:
            with open(getJsonPath("offergrants.json"), 'r') as json_file:
                PACKSDATA = json.load(json_file)

        builtinsDataReq = requests.get("https://api.fecooo.hu/fngg/builtins")
        if builtinsDataReq.status_code == 200:
            BUILTINS = builtinsDataReq.json()
        else:
            with open(getJsonPath("builtinemotes.json"), 'r') as json_file:
                BUILTINS = json.load(json_file)

        PROFILE_ITEMS = [JSONDATA['profileChanges'][0]['profile']['items'][i] for i in JSONDATA['profileChanges'][0]['profile']['items'].keys()]
        PROFILE_ITEMS_CC = [JSONDATA_CC['profileChanges'][0]['profile']['items'][i] for i in JSONDATA_CC['profileChanges'][0]['profile']['items'].keys()]

        filteredItems = list(filter(lambda x: x['templateId'].split(":")[0] in ACCEPTED_COSMETIC_TYPES, PROFILE_ITEMS))
        filteredItems_cc = list(filter(lambda x: x['templateId'].split(":")[0] in ACCEPTED_COSMETIC_TYPES, PROFILE_ITEMS_CC))

        cosmeticsNames = [i['templateId'].split(":")[1].lower() for i in filteredItems]
        builtIns = list(set([BUILTINS[i].lower() for i in BUILTINS.keys() if i.lower() in cosmeticsNames]))
        banners = [i['templateId'].split(":")[1].lower() for i in filteredItems_cc]

        packs = list(set([PACKSDATA[i] for i in PACKSDATA.keys() if i in cosmeticsNames]))

        cosmeticsNames += banners
        cosmeticsNames += builtIns

        fnggDataRequest = requests.get("https://fortnite.gg/api/items.json").json()
        fnggBundleData = requests.get("https://fortnite.gg/api/bundles.json").json()

        FNGG_DATA = {i.lower(): int(fnggDataRequest[i]) for i in fnggDataRequest.keys()}
        ATHENA_CREATION_DATE = JSONDATA['profileChanges'][0]['profile']['created']

        ownedBundles = list(set([CheckBundle(i, fnggBundleData[i], cosmeticsNames, FNGG_DATA) for i in fnggBundleData.keys()]))
        ownedBundles = list(filter(lambda x: x is not None, ownedBundles))

        ints = sorted([i for i in ([FNGG_DATA[it] for it in cosmeticsNames if it in FNGG_DATA] + packs + ownedBundles) if i is not None])

        diff = list(map(lambda e: str(e[1] - ints[e[0] - 1]) if e[0] > 0 else str(e[1]), enumerate(ints)))

        compress = zlib.compressobj(
            level=-1, 
            method=zlib.DEFLATED, 
            wbits=-9,
            memLevel=zlib.DEF_MEM_LEVEL, 
            strategy=zlib.Z_DEFAULT_STRATEGY
        )
        compressed = compress.compress(f"{ATHENA_CREATION_DATE},{','.join(diff)}".encode())
        compressed += compress.flush()

        encoded = base64.urlsafe_b64encode(compressed).decode().rstrip("=")

        locker_url = f"https://fortnite.gg/my-locker?items={encoded}"
        tk.Label(root, text="Your locker:", font=("Helvetica", 12)).pack(pady=5)
        locker_link = tk.Label(root, text="Click here to view your locker",font=underline_font, fg="white", cursor="hand2")
        locker_link.pack(pady=5)
        locker_link.bind("<Button-1>", lambda _: open_link(locker_url))

        with open("locker.txt", "w", encoding="utf-8") as f:
            f.write(locker_url)

    tk.Button(root, text="Start Authentication", command=lambda: asyncio.run_coroutine_threadsafe(authenticate(), loop)).pack(pady=20)

    root.mainloop()
    root.mainloop()

if __name__ == "__main__":
    start_app()
