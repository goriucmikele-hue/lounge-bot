import os, requests
from dotenv import load_dotenv


def main():
    load_dotenv()
    r = requests.post(os.environ["DISCORD_WEBHOOK_URL"], json={"content": "Test bot Lounge: merge!"})
    print("Status:", r.status_code)


if __name__ == "__main__":
    main()