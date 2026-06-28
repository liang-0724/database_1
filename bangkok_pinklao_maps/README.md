# 曼谷 Pinklao 美食地圖 / 行程工具

依需求整理的曼谷 Pinklao 地點工具與行程，含 Google Maps Places API 腳本、KML 產生器，以及四大分類地點資料。

## 結構
```
bangkok_pinklao_maps/
├── data/places.json        # 所有地點的原始資料（含分類、近似座標、備註）
├── fetch_place_ids.py      # 用 Places API 取得 place_id 與精確座標
├── build_kml.py            # 由資料產生 KML 與 place_ids.json
├── output/
│   ├── bangkok_pinklao.kml # 可匯入 Google My Maps 的 KML（4 圖層 / 54 地標）
│   └── place_ids.json      # place_id 清單（JSON）
└── itinerary.md            # 行程摘要（週末/平日晚上/咖啡廳）
```

## 快速開始
```bash
# 1) 直接產生 KML 與 place_id 骨架（不需 API Key）
python3 build_kml.py

# 2) 取得官方 place_id 與精確座標（需有效金鑰，並啟用 Places API）
export GOOGLE_MAPS_API_KEY="你的金鑰"
python3 fetch_place_ids.py
python3 build_kml.py   # 重建 KML，描述帶入 place_id
```

## 重要說明
- 程式只用到 Python 標準函式庫，無需安裝額外套件。
- **Google Maps 沒有公開 API 可把地點寫入個人「已儲存清單」**；本工具走官方支援路徑：產生 KML → 匯入 [Google My Maps](https://www.google.com/maps/d/)。
- 座標、營業時間、花費為概估值，請於出發前再確認。

詳見 [`itinerary.md`](./itinerary.md)。
