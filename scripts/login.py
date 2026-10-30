from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = PROJECT_ROOT / "profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="msedge",
            headless=False,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.zalando-lounge.ro/")
        input("Log in, then press Enter here...")
        ctx.close()

    print("Session saved in:", PROFILE_DIR)


if __name__ == "__main__":
    main()