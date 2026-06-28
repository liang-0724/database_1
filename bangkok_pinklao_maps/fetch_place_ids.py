#!/usr/bin/env python3
"""
使用 Google Maps Places API (Text Search) 為 data/places.json 中的每個地點
取得官方 place_id 與精確座標，並輸出：
  - output/place_ids.json  (所有地點的 place_id 清單)
  - 同時把精確座標回寫到記憶體後可再產生 KML

用法：
  export GOOGLE_MAPS_API_KEY="你的金鑰"
  python fetch_place_ids.py

注意：
  * 需在 Google Cloud Console 啟用 "Places API"。
  * Google Maps 並無公開 API 可將地點寫入個人「清單(已儲存)」；
    正式做法是產生 KML 後匯入 Google My Maps (mymaps.google.com)。
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "places.json")
OUT = os.path.join(HERE, "output", "place_ids.json")

# Places API (New) Text Search endpoint
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"


def search_place(query, api_key):
    """以文字搜尋取得第一筆結果的 place_id / 名稱 / 座標。"""
    body = json.dumps({"textQuery": query, "languageCode": "en"}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Goog-Api-Key", api_key)
    req.add_header(
        "X-Goog-FieldMask",
        "places.id,places.displayName,places.formattedAddress,places.location",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    places = data.get("places") or []
    if not places:
        return None
    p = places[0]
    loc = p.get("location", {})
    return {
        "place_id": p.get("id"),
        "name": (p.get("displayName") or {}).get("text"),
        "formatted_address": p.get("formattedAddress"),
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
    }


def main():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key or api_key.startswith("[") or api_key == "YOUR_API_KEY":
        sys.exit(
            "錯誤：請先設定有效的 GOOGLE_MAPS_API_KEY 環境變數。\n"
            '例如： export GOOGLE_MAPS_API_KEY="AIza..."'
        )

    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    results = {"list_name": data["list_name"], "categories": {}}
    for category, items in data["categories"].items():
        results["categories"][category] = []
        for item in items:
            query = f"{item['name']}, {item['address']}"
            print(f"搜尋: {query}")
            try:
                hit = search_place(query, api_key)
            except Exception as exc:  # noqa: BLE001
                print(f"  ! 失敗: {exc}")
                hit = None
            entry = {
                "name": item["name"],
                "address": item["address"],
                "place_id": hit["place_id"] if hit else None,
                "lat": hit["lat"] if hit else item.get("lat"),
                "lng": hit["lng"] if hit else item.get("lng"),
                "matched_name": hit["name"] if hit else None,
            }
            results["categories"][category].append(entry)
            time.sleep(0.2)  # 友善節流

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n已輸出 place_id 清單 -> {OUT}")
    print("接著執行 python build_kml.py 產生 KML。")


if __name__ == "__main__":
    main()
