import json, random, re, time
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main():
    phrase = "new balance"
    model_re = re.compile(r"1906|2002", re.I)
    sizes = {"41", "41.5", "42"}
    max_lei = 500

    base = "https://www.zalando-lounge.ro/api/phoenix/smart-search/product-listing"
    fetch = """async (u) => { const r = await fetch(u, {credentials:'include'});
      return {status: r.status, body: r.ok ? await r.json() : null}; }"""

    items, cursor = [], None
    with sync_playwright() as p:
        ctx = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
        page = ctx.new_page()
        page.goto("https://www.zalando-lounge.ro/search-catalog?query=new+balance",
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

    nb = [i for i in items if (i.get("brand_name") or "").lower() == "new balance"]
    print(f"\nTotal: {len(items)} | New Balance: {len(nb)}")
    print("NB fără name_prefix:", sum(1 for i in nb if not (i.get('name_prefix') or '').strip()))
    print("Modele NB:", sorted({i.get('name_prefix') for i in nb}))

    print("\nPotriviri 1906/2002 (orice mărime):")
    for i in nb:
        if model_re.search(i.get("name_prefix") or ""):
            av = [s["size"] for s in i["simples"] if s.get("stock_status") == "AVAILABLE"]
            print("-", i["name_prefix"], i["color_name"], i["special_price"]/100, "lei |", av)

    print("\nNB pe mărimile tale, sub buget (orice model):")
    for i in nb:
        av = [s["size"] for s in i["simples"]
              if s["size"] in sizes and s.get("stock_status") == "AVAILABLE"]
        if av and i["special_price"]/100 <= max_lei:
            print("-", i["name_prefix"] or "(fără nume)", i["color_name"], i["special_price"]/100, "lei |", av)


if __name__ == "__main__":
    main()