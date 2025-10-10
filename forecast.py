import yfinance as yf
import numpy as np
from datetime import datetime, timedelta, timezone
import requests
import pandas as pd

# Telegram Bot Configuration
BOT_TOKEN = "8258662771:AAFSexSEzgX6Npw8CeUxU8mYr4weoLZrC20"
CHAT_ID = "1939059559"

# List of coins to forecast
coins = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Dogecoin": "DOGE-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "XRP": "XRP-USD",
    "Sui": "SUI-USD",
    "Pepe": "PEPE-USD"
}

def fetch_data(symbol):
    try:
        data = yf.download(symbol, period="90d", interval="1d")["Close"].dropna()
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def gbm_forecast(prices, days=2):
    log_returns = np.log(prices / prices.shift(1)).dropna()
    mu = log_returns.mean()
    sigma = log_returns.std()
    last_price = prices.iloc[-1]

    forecast = last_price * np.exp((mu - 0.5 * sigma**2) * days + sigma * np.sqrt(days) * np.random.normal())
    pct_change = ((forecast - last_price) / last_price) * 100
    return forecast, pct_change

def generate_signal(change):
    if change > 2:
        return "🟢 BUY"
    elif change < -2:
        return "🔴 SELL"
    else:
        return "⚪ HOLD"

def main():
    results = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for coin, symbol in coins.items():
        print(f"Fetching {coin}...")
        data = fetch_data(symbol)
        if data is None or data.empty:
            results.append((coin, "No Data", "-", "-", "-"))
            continue

        forecast, pct_change = gbm_forecast(data)
        signal = generate_signal(pct_change)
        results.append((coin, f"${data.iloc[-1]:.4f}", f"${forecast:.4f}", f"{pct_change:.2f}%", signal))

    df = pd.DataFrame(results, columns=["Coin", "Current Price", "Forecast (2d)", "% Change", "Signal"])

    # Format message for Telegram
    message = f"📊 *Crypto Forecast Update* — {today}\n\n"
    for _, row in df.iterrows():
        message += (
            f"💠 *{row['Coin']}*\n"
            f"💵 Current: {row['Current Price']}\n"
            f"🔮 Forecast (2d): {row['Forecast (2d)']}\n"
            f"📈 Change: {row['% Change']}\n"
            f"📊 Signal: {row['Signal']}\n\n"
        )
    message += "⚙️ Model: GBM  |  ⏱️ Forecast Horizon: 2 Days"

    # Send to Telegram
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(telegram_url, data=payload)
    print("✅ Telegram update sent.")

if __name__ == "__main__":
    main()
