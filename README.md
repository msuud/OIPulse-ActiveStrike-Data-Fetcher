# OIPulse ActiveStrike Data Fetcher

This project is a Python-based automation tool built to **periodically fetch active strike open interest (OI) data** from [OIPulse](https://www.oipulse.com)'s live options analysis page and store it in a local CSV file for further analysis.

## 🧠 Overview

- This project was developed for a client, who needed to automatically track the live chart data from the OIPulse Active Strikes IV page.
- The goal was to eliminate manual entry by updating the chart data into an Excel file every 5 minutes.
- The solution fetches live API data, filters it, and writes it neatly into a structured Excel file.
- This automation saves time, ensures accuracy, and meets the real-time monitoring need of the client.

OIPulse provides real-time options market data, including strike-level OI values for CE and PE.

This tool solves that by:
- Allowing the user to log in manually to OIPulse once via Chrome browser.
- Saving session cookies and JWT token securely.
- Automatically fetching updated active strike IV and OI data every 5 minutes.
- Saving the data into a structured CSV file for each day.

---

## 🚀 Features

- 🔐 Manual login support with automatic session capture (cookies + token).
- ♻️ Auto-refresh every 5 minutes.
- 🧹 Filters to skip invalid timestamps and only keep valid 5-min data.
- 📁 Saves data in `live_data.csv` per date.
- 🧠 Smart handling of 09:15 missing data (accepts 09:16/09:17 as fallback).
- 📊 Output: Date, Time, Asset Price, CE OI, PE OI, Fetched At.

---

## 🛠️ Technologies Used

- **Python 3**
- **Selenium** for browser automation
- **Requests** for API interaction
- **Pandas** for CSV handling
- **ChromeDriver** for launching browser
- **PyInstaller** (used to build `active-strike.exe`)
