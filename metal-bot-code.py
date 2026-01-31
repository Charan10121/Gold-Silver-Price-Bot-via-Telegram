import cloudscraper
import os
import re
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PRICE_FILE = "last_price.txt"

def clean_price(price_str):
    """Removes '₹', commas, and extra text. Returns clean number string."""
    if not price_str:
        return "N/A"
    # Find the first sequence of digits, optionally with a comma
    match = re.search(r"[\d,]+", price_str)
    if match:
        return match.group(0)
    return price_str

def get_price_from_header(soup, header_pattern):
    """Finds a header matching the pattern, gets the next table, and finds the 1g row."""
    try:
        # 1. Find the header that contains the text (e.g., "24 Carat")
        header = soup.find(lambda tag: tag.name in ["h2", "h3", "h4"] and header_pattern.lower() in tag.get_text().lower())
        
        if not header:
            return "N/A"

        # 2. Find the next table after this header
        table = header.find_next("table")
        if not table:
            return "N/A"

        # 3. Iterate rows to find the "1 gram" entry
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                col0_text = cols[0].get_text().strip().lower()
                # Match "1", "1g", "1 gram", "1 gm"
                if col0_text in ["1", "1g", "1 gram", "1 gm"]:
                    # Price is usually in the 2nd column (index 1)
                    return clean_price(cols[1].get_text())
        
    except Exception as e:
        print(f"Error extracting {header_pattern}: {e}")
    
    return "N/A"

def get_hyderabad_rates():
    scraper = cloudscraper.create_scraper()
    data = {"24K": "N/A", "22K": "N/A", "Silver": "N/A"}

    # --- 1. FETCH GOLD ---
    try:
        url = "https://www.goodreturns.in/gold-rates/hyderabad.html"
        print(f"📡 Fetching Gold from {url}...")
        res = scraper.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Look for headers containing these exact keywords
            data["24K"] = get_price_from_header(soup, "24 Carat")
            data["22K"] = get_price_from_header(soup, "22 Carat")
        else:
            print(f"❌ Gold Request Failed: {res.status_code}")
    except Exception as e:
        print(f"❌ Gold Error: {e}")

    # --- 2. FETCH SILVER ---
    try:
        url = "https://www.goodreturns.in/silver-rates/hyderabad.html"
        print(f"📡 Fetching Silver from {url}...")
        res = scraper.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Look for header "Silver" or "Silver Rate"
            data["Silver"] = get_price_from_header(soup, "Silver")
        else:
            print(f"❌ Silver Request Failed: {res.status_code}")
    except Exception as e:
        print(f"❌ Silver Error: {e}")

    return data

def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("ℹ️ Telegram skipped: Missing keys.")
        return
    
    import requests
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ Telegram Send Error: {e}")

if __name__ == "__main__":
    current_data = get_hyderabad_rates()
    print(f"🔎 Extracted Data: {current_data}")
    
    # Check if we successfully fetched at least one gold price
    if current_data["24K"] != "N/A":
        current_state = f"{current_data['24K']}-{current_data['22K']}-{current_data['Silver']}"
        
        last_state = ""
        if os.path.exists(PRICE_FILE):
            with open(PRICE_FILE, "r") as f:
                last_state = f.read().strip()
        
        if current_state != last_state:
            msg = (f"💰 *Hyderabad Price Update*\n\n"
                   f"🟡 *24K Gold:* ₹{current_data['24K']}/gm\n"
                   f"🟠 *22K Gold:* ₹{current_data['22K']}/gm\n"
                   f"⚪ *Silver:* ₹{current_data['Silver']}/gm\n\n"
                   f"📈 _Price updated on website._")
            
            send_telegram(msg)
            
            with open(PRICE_FILE, "w") as f:
                f.write(current_state)
            print("✅ Update sent to Telegram.")
        else:
            print("ℹ️ Prices unchanged.")
    else:
        print("❌ Failed to scrape valid data. Check website layout.")
