from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.zalando-lounge.ro/")
        print("Page title:", page.title())
        input("If you saw the window and the title, press Enter...")
        browser.close()


if __name__ == "__main__":
    main()