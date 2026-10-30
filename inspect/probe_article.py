import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SKU = "NE242A0M1-Q12"
URL = "https://www.zalando-lounge.ro/campaigns/ZZO4RKD/articles/NE242A0M1-Q12"


def main():
    items = json.loads((DATA_DIR / "full_scan.json").read_text(encoding="utf-8"))
    print("=== În full_scan.json ===")
    for i in items:
        if i["config_sku"] == SKU:
            print(i["campaign_id"], i["special_price"] / 100, "lei |",
                  [(s["size"], s["stock_status"]) for s in i["simples"]])

    found = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("simples"), list):
                found.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    def on_response(resp):
        try:
            if "json" in (resp.headers.get("content-type") or ""):
                walk(json.loads(resp.text()))
        except Exception:
            pass

    with sync_playwright() as p:
        ctx = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
        page = ctx.new_page()
        page.on("response", on_response)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        nd = page.query_selector("script#__NEXT_DATA__")
        if nd:
            walk(json.loads(nd.inner_text()))
        page.close()

    print("\n=== Din pagina de produs ===")
    print("obiecte cu simples:", len(found))
    for o in found[:3]:
        print("chei:", sorted(o.keys()))
        print(json.dumps(o["simples"], ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()