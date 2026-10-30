from playwright.sync_api import sync_playwright

URL = "https://www.zalando-lounge.ro/search-catalog?query=new+balance"
JS = """() => {
  const out = [];
  for (const img of document.querySelectorAll('img')) {
    const src = img.currentSrc || img.src || '';
    if (!src.includes('spp-media')) continue;
    const a = img.closest('a');
    out.push({img: src, href: a ? a.href : null});
    if (out.length >= 3) break;
  }
  return out;
}"""


def main():
    with sync_playwright() as p:
        ctx = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
        page = ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        for r in page.evaluate(JS):
            print(r)
        page.close()


if __name__ == "__main__":
    main()