import json
import os
from datetime import date

FILE = "./retroai/knowledge.json"
PATCH = "16.3"

NEW_TFT_DATA = {
    "ionia yunara wukong comp": {
        "short": "Ionia Yunara & Wukong is a top tier Fast 8 comp.",
        "details": "Carry: Yunara. Items: Guinsoo, IE, LW. Playstyle: Fast 8."
    },
    "demacia garen lux comp": {
        "short": "Demacia Lux & Garen is a stable climbing comp.",
        "details": "Lux items: Blue Buff, JG. Garen items: tank items."
    }
}

# load old data
with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

old_patch = data["meta"].get("patch")

# archive old tft
if old_patch:
    data["archive"][old_patch] = data["tft"]

# update meta
data["meta"]["patch"] = PATCH
data["meta"]["last_update"] = str(date.today())

# update tft only
data["tft"] = NEW_TFT_DATA

# save
os.makedirs("./retroai", exist_ok=True)
with open(FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("TFT updated safely to patch", PATCH)

