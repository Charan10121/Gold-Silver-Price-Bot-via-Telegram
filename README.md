# Gold & Silver Price Telegram Bot

A Python automation script that monitors daily Gold (24K/22K) and Silver rates in **Hyderabad** using web scraping. If a price change is detected compared to the last check, it sends a formatted alert to a Telegram chat.

## 🚀 Features
* **Web Scraping:** Robust extraction of prices from `goodreturns.in` using `cloudscraper` (bypasses Cloudflare protection) and `BeautifulSoup`.
* **Smart Alerts:** Only sends a notification if prices have changed since the last run.
* **Change Tracking:** Calculates and displays the price difference (e.g., `+₹50 🔺` or `-₹10 🔻`).
* **Automated Schedule:** Runs automatically via GitHub Actions (cron job).

## 🛠️ Tech Stack
* **Python 3.x**
* **Libraries:** `cloudscraper`, `beautifulsoup4`, `requests`
* **CI/CD:** GitHub Actions (for scheduling)

DISCLAIMER: This project is for educational purposes only.
