import json
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
URL = "https://www.zalando-lounge.ro/search-catalog?query=new+balance+1906"


def main():
    saved = []

    def on_response(resp):
        try:
            if "json" not in (resp.headers.get("content-type") or ""):
                return
            body = resp.text()
            if '"simples"' not in body and '"config_sku"' not in body:
                return
            n = len(saved) + 1
            (DATA_DIR / f"grid_{n}.json").write_text(body, encoding="utf-8")
            saved.append(resp.url)
            print(f"[{n}] salvat: {resp.url[:160]}")
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        page = ctx.new_page()
        page.on("response", on_response)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        for _ in range(8):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)

        nd = page.query_selector("script#__NEXT_DATA__")
        if nd:
            (DATA_DIR / "next_data.json").write_text(nd.inner_text(), encoding="utf-8")
            print("salvat și __NEXT_DATA__")

        page.close()

    (DATA_DIR / "urls.txt").write_text("\n".join(saved), encoding="utf-8")
    print(f"Gata: {len(saved)} răspunsuri de grid salvate în {DATA_DIR}")


if __name__ == "__main__":
    main()