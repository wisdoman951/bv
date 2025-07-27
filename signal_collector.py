import time
import random
from datetime import datetime, timedelta
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://agile-cliffs-23967.herokuapp.com"
EXCEL_FILE = "signals_log.xlsx"


def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    return driver


def get_table(driver: webdriver.Chrome) -> pd.DataFrame:
    html = driver.page_source
    tables = pd.read_html(html)
    if tables:
        return tables[0]
    return pd.DataFrame()


def fetch_price(symbol: str) -> float:
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return float(resp.json().get("price", 0))
    except Exception:
        pass
    return 0.0


def read_existing() -> pd.DataFrame:
    try:
        return pd.read_excel(EXCEL_FILE)
    except Exception:
        return pd.DataFrame(
            columns=["Coin", "Price", "Stop Loss", "Take Profit", "UTC Time", "寄送狀態"]
        )


def append_signal(data: dict):
    df = read_existing()
    df = df.append(data, ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)


def recently_sent(df: pd.DataFrame, coin: str, now: datetime) -> bool:
    if df.empty:
        return False
    cutoff = now - timedelta(hours=12)
    recent = df[(df["Coin"] == coin) & (df["UTC Time"] >= cutoff) & df["寄送狀態"].str.contains("寄送")]
    return not recent.empty


def main():
    driver = init_driver()
    while True:
        df_table = get_table(driver)
        if not df_table.empty:
            existing = read_existing()
            for _, row in df_table.iterrows():
                try:
                    coin = str(row["Coin"])
                    pings = int(row["Pings"])
                    net_vol = float(str(row["Net Vol %"]).replace("%", ""))
                except Exception:
                    continue
                if pings >= 5 and net_vol >= 3:
                    symbol = coin.upper() + "USDT"
                    price = fetch_price(symbol)
                    if not price:
                        continue
                    sl_ratio = random.uniform(0.015, 0.025)
                    tp_ratio = random.uniform(0.02, 0.03)
                    sl = price * (1 - sl_ratio)
                    tp = price * (1 + tp_ratio)
                    now = datetime.utcnow()
                    status = "未寄送"
                    if recently_sent(existing, coin, now):
                        status = "12小時內已寄送"
                    append_signal({
                        "Coin": coin,
                        "Price": price,
                        "Stop Loss": sl,
                        "Take Profit": tp,
                        "UTC Time": now,
                        "寄送狀態": status
                    })
        time.sleep(60)


if __name__ == "__main__":
    main()
