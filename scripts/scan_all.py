import json, os, random, time
import sys
from pathlib import Path
from urllib.parse import quote
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from search_config import select_preset

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def matching_products(items, preset):
    brand = str(preset.get("brand") or "").strip().casefold()
    terms = [str(term).strip().casefold() for term in preset.get("model_terms", []) if str(term).strip()]
    wanted_sizes = {str(size).strip() for size in preset.get("sizes", [])}
    category = str(preset.get("category") or "").strip().casefold()
    max_price = float(preset.get("max_lei", 0))
    matches = []

    for item in items:
        item_brand = str(item.get("brand_name") or "").strip().casefold()
        if brand and brand not in item_brand:
            continue
        name = str(item.get("name_prefix") or "").casefold()
        if terms and not any(term in name for term in terms):
            continue
        category_text = " ".join([str(item.get("tag") or ""), name]).casefold()
        if category and category not in category_text:
            continue
        available_sizes = [
            str(simple.get("size"))
            for simple in item.get("simples", [])
            if simple.get("stock_status") == "AVAILABLE"
            and (not wanted_sizes or str(simple.get("size")) in wanted_sizes)
        ]
        price_cents = item.get("special_price")
        if not available_sizes or price_cents is None or price_cents / 100 > max_price:
            continue
        matches.append((item, available_sizes))
    return matches


def send_announcements(matches, preset):
    load_dotenv(PROJECT_ROOT / ".env")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL is not set; skipping Discord announcements.")
        return

    search_url = f"https://www.zalando-lounge.ro/search-catalog?query={quote(preset['phrase'])}"
    announcements = []
    for item, sizes in matches:
        name = " ".join(part for part in [item.get("brand_name"), item.get("name_prefix"), item.get("color_name")] if part)
        price = item["special_price"] / 100
        announcements.append(
            f"**{name}**\n"
            f"Price: {price:.2f} lei | Available sizes: {', '.join(sizes)}\n"
            f"SKU: {item.get('config_sku') or item.get('model_sku') or 'n/a'} | Campaign: {item.get('campaign_id') or 'n/a'}\n"
            f"[Search Zalando Lounge]({search_url})"
        )

    chunks = []
    current_chunk = ""
    for announcement in announcements:
        candidate = f"{current_chunk}\n\n{announcement}" if current_chunk else announcement
        if len(candidate) > 1800 and current_chunk:
            chunks.append(current_chunk)
            current_chunk = announcement
        else:
            current_chunk = candidate
    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        response = requests.post(webhook_url, json={"content": chunk}, timeout=20)
        response.raise_for_status()
    print(f"Sent {len(matches)} product announcement(s) in {len(chunks)} Discord message(s).")


def main():
    preset_name = sys.argv[1] if len(sys.argv) > 1 else None
    preset_name, preset = select_preset(preset_name)
    phrase = preset["phrase"]

    base = "https://www.zalando-lounge.ro/api/phoenix/smart-search/product-listing"
    fetch = """async (u) => { const r = await fetch(u, {credentials:'include'});
      return {status: r.status, body: r.ok ? await r.json() : null}; }"""

    items, cursor = [], None
    with sync_playwright() as p:
        ctx = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
        page = ctx.new_page()
        page.goto(f"https://www.zalando-lounge.ro/search-catalog?query={quote(phrase)}",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        for n in range(30):
            url = f"{base}?phrase={quote(phrase)}&size=60&new_dead_ends=true"
            if cursor:
                url += f"&cursor={quote(cursor)}"
            r = page.evaluate(fetch, url)
            if r["status"] != 200:
                print("oprit, status", r["status"]); break
            body = r["body"]
            items += body.get("results") or []
            cursor = body.get("next_cursor")
            print(f"pagina {n+1}: {len(items)} produse")
            if not cursor:
                break
            time.sleep(random.uniform(2, 5))
        page.close()

    (DATA_DIR / "full_scan.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

    brand = str(preset.get("brand") or phrase).casefold()
    brand_items = [i for i in items if brand in str(i.get("brand_name") or "").casefold()]
    print(f"\nTotal: {len(items)} | {phrase.title()}: {len(brand_items)}")
    print(f"{phrase.title()} fără name_prefix:", sum(1 for i in brand_items if not (i.get('name_prefix') or '').strip()))
    print("Modele:", sorted({i.get('name_prefix') for i in brand_items}))

    matches = matching_products(items, preset)
    print(f"\nMatching products (model, available size, and price): {len(matches)}")
    for item, sizes in matches:
        print(f"- {item.get('name_prefix') or '(no name)'} | {item.get('color_name')} | {item['special_price'] / 100:.2f} lei | {sizes}")
    send_announcements(matches, preset)


if __name__ == "__main__":
    main()