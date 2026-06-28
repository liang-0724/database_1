#!/usr/bin/env python3
"""由 data/places.json 產生一份「點了就能存」的 Markdown 清單。
每個地點是 Google Maps 搜尋連結，點開即顯示該地點，可直接按「儲存」加入清單。
輸出：output/manual_pick_list.md
"""
import json
import os
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "places.json")
OUT = os.path.join(HERE, "output", "manual_pick_list.md")

EMOJI = {
    "曼谷 Pinklao 美食地圖": "🍜",
    "週末景點": "🗺️",
    "平日晚上": "🌃",
    "咖啡廳": "☕",
}


def maps_link(name, address):
    q = urllib.parse.quote_plus(f"{name} {address}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    lines = [f"# {data['list_name']}｜手動加入清單", ""]
    lines.append("> 點地點名稱 → 在 Google Maps 開啟 → 按「儲存」加入你的清單。")
    lines.append("")
    total = 0
    for cat, items in data["categories"].items():
        e = EMOJI.get(cat, "📍")
        lines.append(f"## {e} {cat}（{len(items)} 個）")
        lines.append("")
        for i, it in enumerate(items, 1):
            total += 1
            link = maps_link(it["name"], it["address"])
            note = f" — {it['notes']}" if it.get("notes") else ""
            lines.append(f"{i}. **[{it['name']}]({link})**{note}")
        lines.append("")
    lines.insert(2, f"> 共 {total} 個地點。")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"已輸出 -> {OUT}（{total} 個地點）")


if __name__ == "__main__":
    main()
