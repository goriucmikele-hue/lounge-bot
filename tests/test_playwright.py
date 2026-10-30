from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.zalando-lounge.ro/")
        print("Titlu pagină:", page.title())
        input("Dacă ai văzut fereastra și titlul, apasă Enter...")
        browser.close()


if __name__ == "__main__":
    main()