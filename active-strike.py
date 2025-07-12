import json
import os
import time
import requests
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COOKIE_FILE = "cookies.json"
TOKEN_FILE = "token.json"
CSV_FILE = "live_data.csv"
TARGET_URL = "https://www.oipulse.com/app/options-analysis/active-strikes-iv"
API_URL = "https://api.oipulse.com/api/active-strike-oi/getselectedactivestrikeivalldata"

driver = None 


def capture_cookies_and_token():
    global driver
    print("Opening browser for manual login...\n")
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get(TARGET_URL)
    print("After login, go to:")
    print(TARGET_URL)
    print("!! IMPORTANT -- Select NIFTY")
    print("Waiting for manual login... 60 sec")
    time.sleep(60)

    # Save cookies
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f)
    print("Cookies saved successfully.")

    # Save token
    try:
        token = driver.execute_script("return localStorage.getItem('token');")
        if token:
            with open(TOKEN_FILE, "w") as f:
                json.dump({"token": token}, f)
            print("Token saved successfully.")
        else:
            print("Access token not found.")
    except Exception as e:
        print("Error extracting token:", e)

    print("Browser remains open.")


def load_cookie_string():
    if not os.path.exists(COOKIE_FILE):
        return {}
    try:
        with open(COOKIE_FILE, "r") as f:
            cookies = json.load(f)
        return {cookie['name']: cookie['value'] for cookie in cookies}
    except Exception as e:
        print("! Failed to load cookies:", str(e))
        return {}


def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f).get("token")


def write_to_csv(data):
    records = []
    today = datetime.now().strftime("%Y-%m-%d")

    # Load existing data (if any)
    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        df_old = df_old[df_old['Date'] == today]
    else:
        df_old = pd.DataFrame(columns=["Date", "Time", "Asset Price", "CE", "PE", "Fetched At"])

    for item in data:
        time_stamp = item.get("stTime")
        try:
            dt_time = datetime.strptime(time_stamp, "%H:%M:%S")
            minute = dt_time.minute
        except:
            continue

        # Allow the first row even if it's 09:16 or 09:17 (assume 09:15)
        if df_old.empty and dt_time.hour == 9 and minute in [16, 17]:
            print("⚠️ Replacing missing 09:15 with available:", time_stamp)
        elif minute % 5 != 0:
            continue  # Skip non-5-min data

        price = item.get("inAssetPrice")
        ce = item.get("obOiData", [{}])[0].get("CE")
        pe = item.get("obOiData", [{}])[1].get("PE")

        records.append({
            "Date": today,
            "Time": time_stamp,
            "Asset Price": price,
            "CE": ce,
            "PE": pe,
            "Fetched At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    if not records:
        print("No valid 5-minute data to write.")
        return

    df_new = pd.DataFrame(records)

    # Combine and drop duplicates
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    df_combined.drop_duplicates(subset=["Date", "Time"], keep="last", inplace=True)

    df_combined.to_csv(CSV_FILE, index=False)
    print(f"CSV updated. Total rows: {len(df_combined)}.")



def fetch_data():
    token = load_token()
    if not token:
        print("! No token found.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    cookies = load_cookie_string()
    if not cookies:
        print("! No cookies found.")
        return

    payload = {
        "stSelectedAsset": "NIFTY",  
        "stSelectedAvailableDate": datetime.now().strftime("%Y-%m-%d"),
        "stSelectedModeOfData": "live"
    }

    print("Fetching data...")
    try:
        response = requests.post(API_URL, headers=headers, cookies=cookies, json=payload)
        # print("Raw response\n")

        data = response.json()
        if data.get("status") == "success":
            print("Data fetched successfully.")
            write_to_csv(data.get("data", []))
        elif data.get("msg") == "!! Cookie has expired. Please login again.":
            print("Unauthorized. Opening the browser again for you to login...")
            os.remove(COOKIE_FILE)
            os.remove(TOKEN_FILE)
            capture_cookies_and_token()
            fetch_data()
        else:
            print("! Unexpected response:", data)
    except Exception as e:
        print("! Failed to decode response:", str(e))


def main_loop():
    if not os.path.exists(TOKEN_FILE) or not os.path.exists(COOKIE_FILE):
        print("Login required.")
        capture_cookies_and_token()

    while True:
        fetch_data()
        print("Refreshing for 5 minutes...\n")
        time.sleep(300)


if __name__ == "__main__":
    main_loop()
