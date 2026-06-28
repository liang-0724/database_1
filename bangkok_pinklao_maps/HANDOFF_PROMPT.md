# 筆電接手用 Prompt（複製以下整段給 AI 編碼助理）

---

我要在曼谷 Pinklao 區做一份旅遊地圖工具，請用 **Python（只用標準函式庫）** 幫我重建並執行。我住在 CASA 17 Hotel（Soi Somdet Phra Pin Klao 17, Arun Amarin, Bangkok Noi），緊鄰 Central Pinklao。

## 背景與已知限制（請照做，不要重提這兩點當作障礙）
1. Google Maps **沒有**公開 API 能把地點寫進個人「已儲存清單」。官方支援路徑是：產生 **KML → 匯入 Google My Maps (https://www.google.com/maps/d/)**，每個分類成為一個圖層。
2. 取得官方 `place_id` 需要有效的 Google Maps API Key 並啟用 **Places API (New)**。我的金鑰：`填入你的真實金鑰`

## 請建立的專案結構
```
bangkok_pinklao_maps/
├── data/places.json        # 所有地點：分類 / 近似座標 / 備註
├── fetch_place_ids.py      # 用 Places API Text Search 取 place_id 與精確座標
├── build_kml.py            # 由資料產生 KML + place_ids.json
├── output/bangkok_pinklao.kml
├── output/place_ids.json
└── itinerary.md            # 行程摘要
```

## 地點資料（4 個分類，共 54 個地標）

### 分類 A「曼谷 Pinklao 美食地圖」(橘)
1. Maruay Food Hall — 124 Borommaratchachonnani Rd, Bangkok Noi
2. Indy Market Pinklao — 209 Charan Sanit Wong Rd, Bang Phlat
3. Central Pinklao — 7/222 Borommaratchachonnani Rd, Arun Amarin, Bangkok Noi
4. Onkijung Central Pinklao — Central Pinklao G 樓（韓式烤肉）
5. The Stone Central Pinklao — Central Pinklao 5 樓
6. CASA 17 Hotel — Soi Somdet Phra Pin Klao 17（住宿基地）

### 分類 B「週末景點」(紅) — 4 個週末 × 2 天，每點附推薦餐廳
- 週末1 老城+河岸：大皇宮&玉佛寺 / 臥佛寺 / Tha Maharaj ；鄭王廟 / ICONSIAM / The Jam Factory
  - 美食：Err Urban Rustic Thai、Pa Aew、Savoey、SookSiam 美食街、The Never Ending Summer
- 週末2 恰圖恰+現代曼谷：Chatuchak 週末市集 / Or Tor Kor / Ari ；Terminal 21 / EmSphere / Benjakitti 森林公園
  - 美食：椰子冰淇淋、Or Tor Kor 海鮮芒果糯米、Pier 21、EmSphere Food Hall
- 週末3 唐人街+河岸：Yaowarat / 金佛寺 Wat Traimit / Talat Noi ；Asiatique / Lhong 1919
  - 美食：T&K Seafood、Nai Ek 豬肉粥、Hong Sieng Kong、Baan Khanitha
- 週末4 綠肺+老城：Bang Krachao 單車 / Bang Nam Phueng 水上市場 ；Phra Athit Road / Khaosan Road
  - 美食：水上市場炭烤甜點、Krua Apsorn、Jok Pochana

### 分類 C「平日晚上」(藍) — 20 個 ≤30 分車程，標營業時間/交通/花費(THB)
Indy Market(17:00–23:00,步行10分,150–300)、Central Pinklao(10:00–22:00,步行5–10分,200–400)、Sena Fest、Tha Maharaj、Wang Lang Market(08:00–20:00,Grab10分,100–250)、Phra Athit Road、Khaosan Road、Yodpiman River Walk、Pak Khlong 花市(24h,Grab20分,50–200)、Saphan Phut 夜市(19:00–24:00)、ICONSIAM(燈光秀)、The Jam Factory、Lhong 1919、Tha Tien & The Deck(看鄭王廟夜景,400–800)、Banglamphu、Tha Phra/The Mall、Riva Surya、Bang Phlat 咖啡街、The Sense Pinklao、Supreme Pinklao。

### 分類 D「咖啡廳」(綠) — 標營業時間/是否販豆/烘焙風格/招牌
1. Factory Coffee (Phaya Thai) — 08:30–18:00,販多國單品淺中焙,招牌手沖
2. Roots Coffee (ICONSIAM) — 10:00–22:00,自家烘焙泰北+進口,拿鐵/黑糖
3. Gallery Drip Coffee (BACC) — 10:30–19:30,單品手沖豆淺焙
4. Hands and Heart (Khlong San,離 Pinklao 近) — 08:00–17:00,競標級單品淺焙,Espresso Tonic
5. Pacamara (Ari) — 07:00–20:00,自家綜合+單品中焙,Dirty/冷萃
6. Karb Coffee (Bang Phlat)、7. The Coffee Cup Pinklao — 在地,販泰國本地豆

## 程式需求
- `data/places.json`：每筆含 name / address / lat / lng（近似座標即可，供 KML 定位）/ notes。
- `fetch_place_ids.py`：對 `places:searchText` 端點 POST，標頭帶 `X-Goog-Api-Key` 與 `X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.location`；逐點取第一筆結果的 place_id 與座標，輸出 `output/place_ids.json`。從環境變數 `GOOGLE_MAPS_API_KEY` 讀金鑰，若是空值或佔位字串就報錯。
- `build_kml.py`：讀 `places.json`（若存在 `place_ids.json` 則優先採用其精確座標/place_id），輸出 KML：`<Document>` 內每個分類一個 `<Folder>`，每點一個 `<Placemark>`（含 name、description=地址+備註+place_id、`<Point><coordinates>lng,lat,0</coordinates>`），每分類用不同 IconStyle 顏色。需 XML 跳脫。
- KML 與 place_id JSON 為主要交付，另寫 `itinerary.md` 行程摘要。
- 全部座標/營業時間/花費標註為概估值。

## 執行步驟
```bash
cd bangkok_pinklao_maps
python3 build_kml.py                       # 先產生 KML（不需金鑰）
export GOOGLE_MAPS_API_KEY="填入你的真實金鑰"
python3 fetch_place_ids.py                 # 取得官方 place_id
python3 build_kml.py                       # 重建 KML，描述帶入 place_id
```
完成後請告訴我地標總數，並說明如何把 `output/bangkok_pinklao.kml` 匯入 Google My Maps。

---
（以上整段即為可貼上的 prompt）
