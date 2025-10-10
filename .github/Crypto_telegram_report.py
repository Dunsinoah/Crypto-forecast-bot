import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

# Telegram credentials from GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# List of coins to forecast
coins = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "DOGE-USD": "Dogecoin",
    "BNB-USD": "Binance Coin",
    "SOL-USD": "Solana",
    "XRP-USD": "XRP",
    "PEPE-USD": "Pepe",
    "SUI-USD": "Sui"
}

def get_forecast(symbol):
    """Fetch last 90 days and forecast short-term trend."""
    try:
        data = yf.download(symbol, period="90d", interval="1d")["Close"]
        if data.isnull().all():
            raise ValueError("No valid data")

        # Simple moving average + slope for trend
        last_price = data.iloc[-1]
        sma_7 = data.rolling(7).mean().iloc[-1]
        slope = np.polyfit(range(len(data[-7:])), data[-7:], 1)[0]
        forecast_price = last_price + slope * 2  # 2-day projection
        pct_change = ((forecast_price - last_price) / last_price) * 100

        # Basic buy/sell signal logic
        if pct_change > 1:
            signal = "BUY 🔼"
        elif pct_change < -1:
            signal = "SELL 🔽"
        else:
            signal = "HOLD ⚖️"

        return {
            "Price": round(last_price, 4),
            "Forecast": round(forecast_price, 4),
            "Change": round(pct_change, 2),
            "Signal": signal
        }
    except Exception as e:
        return {"Price": "N/A", "Forecast": "N/A", "Change": "N/A", "Signal": "No Data"}

def send_telegram_message(message):
    """Send message to Telegram chat."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def main():
    report = []
    for symbol, name in coins.items():
        print(f"Fetching {name}...")
        res = get_forecast(symbol)
        report.append(f"<b>{name}</b>\nPrice: ${res['Price']}\n2d Forecast: ${res['Forecast']}\nChange: {res['Change']}%\nSignal: {res['Signal']}\n")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    message = f"📊 <b>Daily Crypto Forecast - {today}</b>\n\n" + "\n".join(report)
    send_telegram_message(message)
    print("✅ Telegram update sent.")

if __name__ == "__main__":
    main()
