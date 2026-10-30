import json, random, sys, time, collections
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main():
    phrase = sys.argv[1] if len(sys.argv) > 1 else "vans"
    base = "https://www.zalando-lounge.ro/api/phoenix/smart-search/product-listing"
    fetch = """async (u) => { const r = await fetch(u, {credentials:'include'});
      return {status: r.status, body: r.ok ? await r.json() : null}; }"""
    words = ("sneakers", "pantofi", "ghete", "încălțăminte", "sandale", "bocanci", "espadrile")

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
            items += r["body"].get("results") or []
            cursor = r["body"].get("next_cursor")
            print(f"pagina {n+1}: {len(items)} produse")
            if not cursor:
                break
            time.sleep(random.uniform(2, 5))
        page.close()

    out = DATA_DIR / f"scan_{phrase.replace(' ', '_')}.json"
    out.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

    print("\nBranduri:", collections.Counter(i.get("brand_name") for i in items).most_common(5))
    shoes = [i for i in items if any(w in (i.get("tag") or "").lower() for w in words)]
    print("Pantofi:", len(shoes), "din", len(items))
    print("\nMărimi distincte la pantofi:",
          sorted({s["size"] for i in shoes for s in i["simples"]}))
    print()
    for i in shoes:
        print(f'{i.get("name_prefix") or "(gol)":<24} {i.get("gender"):<7} {i["special_price"]/100:>5.0f} lei | '
              f'{[s["size"] for s in i["simples"]]} | {i["config_sku"]} {i["campaign_id"]}')


if __name__ == "__main__":
    main()