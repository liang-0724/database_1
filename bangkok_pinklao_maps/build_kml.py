#!/usr/bin/env python3
"""
由 data/places.json 產生可匯入 Google My Maps 的 KML 檔。
若 output/place_ids.json 存在，會優先採用其中的精確座標與 place_id。

輸出：
  - output/bangkok_pinklao.kml   (依分類分資料夾，每筆一個地標)
  - output/place_ids.json        (若尚未由 fetch_place_ids.py 產生，則建立含 null place_id 的骨架)

匯入方式：
  1. 開啟 https://www.google.com/maps/d/  (Google My Maps)
  2. 建立新地圖 -> 匯入 -> 選擇 bangkok_pinklao.kml
  3. 每個分類會成為一個圖層 (週末景點 / 平日晚上 / 咖啡廳 等)
"""
import json
import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "places.json")
PLACE_IDS = os.path.join(HERE, "output", "place_ids.json")
KML_OUT = os.path.join(HERE, "output", "bangkok_pinklao.kml")
IDS_OUT = os.path.join(HERE, "output", "place_ids.json")

# 各分類的圖示顏色 (KML 樣式)
STYLE_COLORS = {
    "曼谷 Pinklao 美食地圖": "ff2dc0fb",  # 橘
    "週末景點": "ff0000ff",              # 紅
    "平日晚上": "ffff7800",              # 藍
    "咖啡廳": "ff00aa55",                # 綠
}
DEFAULT_COLOR = "ff999999"


def load_place_ids():
    if not os.path.exists(PLACE_IDS):
        return {}
    with open(PLACE_IDS, encoding="utf-8") as f:
        data = json.load(f)
    index = {}
    for cat, items in data.get("categories", {}).items():
        for it in items:
            index[(cat, it["name"])] = it
    return index


def style_block(category):
    color = STYLE_COLORS.get(category, DEFAULT_COLOR)
    sid = "style_" + str(abs(hash(category)) % 100000)
    block = (
        f'    <Style id="{sid}">\n'
        f"      <IconStyle>\n"
        f"        <color>{color}</color>\n"
        f"        <scale>1.1</scale>\n"
        f"        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/dining.png</href></Icon>\n"
        f"      </IconStyle>\n"
        f"    </Style>\n"
    )
    return sid, block


def placemark(item, overrides, style_id):
    name = item["name"]
    o = overrides.get(name, {})
    lat = o.get("lat") or item.get("lat")
    lng = o.get("lng") or item.get("lng")
    place_id = o.get("place_id")
    desc_parts = [item.get("address", "")]
    if item.get("notes"):
        desc_parts.append(item["notes"])
    if place_id:
        desc_parts.append(f"place_id: {place_id}")
        desc_parts.append(
            f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        )
    desc = escape("\n".join(p for p in desc_parts if p))
    return (
        f"      <Placemark>\n"
        f"        <name>{escape(name)}</name>\n"
        f"        <description>{desc}</description>\n"
        f"        <styleUrl>#{style_id}</styleUrl>\n"
        f"        <Point><coordinates>{lng},{lat},0</coordinates></Point>\n"
        f"      </Placemark>\n"
    )


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    overrides = load_place_ids()

    styles = []
    folders = []
    ids_skeleton = {"list_name": data["list_name"], "categories": {}}

    for category, items in data["categories"].items():
        sid, sblock = style_block(category)
        styles.append(sblock)
        marks = [placemark(it, overrides, sid) for it in items]
        folders.append(
            f"    <Folder>\n"
            f"      <name>{escape(category)}</name>\n"
            + "".join(marks)
            + f"    </Folder>\n"
        )
        ids_skeleton["categories"][category] = [
            {
                "name": it["name"],
                "address": it["address"],
                "place_id": overrides.get(it["name"], {}).get("place_id"),
                "lat": overrides.get(it["name"], {}).get("lat") or it.get("lat"),
                "lng": overrides.get(it["name"], {}).get("lng") or it.get("lng"),
            }
            for it in items
        ]

    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "  <Document>\n"
        f"    <name>{escape(data['list_name'])}</name>\n"
        f"    <description>{escape(data.get('note', ''))}</description>\n"
        + "".join(styles)
        + "".join(folders)
        + "  </Document>\n"
        "</kml>\n"
    )

    os.makedirs(os.path.dirname(KML_OUT), exist_ok=True)
    with open(KML_OUT, "w", encoding="utf-8") as f:
        f.write(kml)
    print(f"已輸出 KML -> {KML_OUT}")

    if not os.path.exists(IDS_OUT) or not overrides:
        with open(IDS_OUT, "w", encoding="utf-8") as f:
            json.dump(ids_skeleton, f, ensure_ascii=False, indent=2)
        print(f"已輸出 place_id 清單 (骨架) -> {IDS_OUT}")


if __name__ == "__main__":
    main()
