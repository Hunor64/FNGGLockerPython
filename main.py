import json
import zlib
import base64
import requests

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

# getting the json data of the profile (TODO: API)
JSONDATA = json.load(open("data.json", encoding="utf-8"))
JSONDATA_CC = json.load(open("common_core.json", encoding="utf-8"))

# getting the items from profile as objects
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
fnggDataRequest = requests.get("https://fortnite.gg/api/items.json").json()

FNGG_DATA = {i.lower(): int(fnggDataRequest[i]) for i in fnggDataRequest.keys()}
ATHENA_CREATION_DATE = "2020-10-10T00:00:00.000Z"

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
encoded = base64.urlsafe_b64encode(compressed).decode().rstrip("=")
url = f"https://fortnite.gg/my-locker?items={encoded}"


print(url)

