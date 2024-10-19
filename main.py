import zlib
import base64
import requests
from colorama import Fore
from colored import fg

from helpers import *

zold=fg('green')

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

print(Fore.WHITE + "--> Login to your account on" + Fore.LIGHTGREEN_EX + " https://www.epicgames.com " + Fore.WHITE + "and open this site (" + Fore.LIGHTGREEN_EX + "https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code" + Fore.WHITE + "), then copy the value of " + Fore.LIGHTYELLOW_EX + "'authorization_code'")
AUTH_CODE = input(Fore.WHITE + "--> Paste it here: " + Fore.LIGHTYELLOW_EX)

TOKEN_DATA = GenerateBearerToken(AUTH_CODE)

class User:
    UserName = TOKEN_DATA["displayName"]
    AccessToken = TOKEN_DATA["access_token"]

print(Fore.WHITE + f"\n--> Username: " + Fore.LIGHTBLUE_EX + User.UserName)

print(Fore.WHITE + "\n--> Requesting" + Fore.LIGHTMAGENTA_EX + " athena profile " + Fore.WHITE + "of " + Fore.LIGHTBLUE_EX + User.UserName)
JSONDATA = QueryProfile("athena", User.AccessToken)

print(Fore.WHITE + "--> Requesting" + Fore.LIGHTMAGENTA_EX + " common_core profile " + Fore.WHITE + "of " + Fore.LIGHTBLUE_EX + User.UserName)
JSONDATA_CC = QueryProfile("common_core", User.AccessToken)

# getting the items from profile as objects
print(Fore.WHITE + "\n--> Processing data")
PROFILE_ITEMS = [JSONDATA['profileChanges'][0]['profile']['items'][i] for i in JSONDATA['profileChanges'][0]['profile']['items'].keys()]
PROFILE_ITEMS_CC = [JSONDATA_CC['profileChanges'][0]['profile']['items'][i] for i in JSONDATA_CC['profileChanges'][0]['profile']['items'].keys()]

# filtering items based on the ACCEPTED_COSMETIC_TYPES
filteredItems = list(filter(lambda x: x['templateId'].split(":")[0] in ACCEPTED_COSMETIC_TYPES, PROFILE_ITEMS))
filteredItems_cc = list(filter(lambda x: x['templateId'].split(":")[0] in ACCEPTED_COSMETIC_TYPES, PROFILE_ITEMS_CC))

# cosmetic names from the objects
cosmeticsNames = [i['templateId'].split(":")[1].lower() for i in filteredItems]
banners = [i['templateId'].split(":")[1].lower() for i in filteredItems_cc]

cosmeticsNames += banners

# ----- WORKING WITH THE PREPARED DATA -----

# requesting fngg ids
print(Fore.WHITE + "\n--> Requesting data from " + Fore.LIGHTGREEN_EX + "https://fortnite.gg")
fnggDataRequest = requests.get("https://fortnite.gg/api/items.json").json()

print(Fore.WHITE + "\n--> Processing data")
FNGG_DATA = {i.lower(): int(fnggDataRequest[i]) for i in fnggDataRequest.keys()}
ATHENA_CREATION_DATE = JSONDATA['profileChanges'][0]['profile']['created']

# getting the fngg ids of the items
ints = sorted([FNGG_DATA[it] for it in cosmeticsNames if it in FNGG_DATA])

# compress data
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

# encoding the compressed data to base64
print(Fore.WHITE + "\n--> Encoding data")
encoded = base64.urlsafe_b64encode(compressed).decode().rstrip("=")

print(Fore.WHITE + "\n\n--> Your locker: " + Fore.LIGHTGREEN_EX + f"https://fortnite.gg/my-locker?items={encoded}" + Fore.WHITE)

f = open("locker.txt", "w", encoding="utf-8")
f.write(f"https://fortnite.gg/my-locker?items={encoded}")
f.close()

input()