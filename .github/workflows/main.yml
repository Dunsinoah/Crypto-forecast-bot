# 🚀 Crypto Telegram Forecast Bot (for GitHub / VPS)
import os
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Telegram credentials (stored as environment variables)
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# Coins to track
coins = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "dogecoin": "Dogecoin",
    "binancecoin": "Binance Coin",
    "solana": "Solana",
    "ripple": "XRP",
    "pepe": "Pepe",
    "sui": "Sui"
}

cg = CoinGeckoAPI()
results = []

for coin_id, name in coins.items():
    try:
        data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=90)['prices']
        df = pd.DataFrame(data, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        prices = df['price']
        log_returns = np.log(prices / prices.shift(1)).dropna()
        mu = log_returns.mean()
        sigma = log_returns.std()
        last_price = prices.iloc[-1]

        # 2-day forecast using GBM
        days = 2
        forecast_price = last_price * np.exp((mu - 0.5 * sigma**2) * days + sigma * np.sqrt(days) * np.random.randn())
        pct_change = ((forecast_price - last_price) / last_price) * 100

        if pct_change > 1.0:
            signal = "BUY ✅"
        elif pct_change < -1.0:
            signal = "SELL ❌"
        else:
            signal = "HOLD ⚖️"

        results.append([name, round(last_price, 4), round(forecast_price, 4), round(pct_change, 2), signal])

    except Exception as e:
        results.append([name, "Error", "Error", "Error", str(e)[:30]])

df = pd.DataFrame(results, columns=["Coin", "Current Price (USD)", "Forecast (2d)", "% Change", "Signal"])

# --- Generate PDF ---
pdf_path = "crypto_forecast_report.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)
c.setFont("Helvetica-Bold", 14)
c.drawString(160, 750, "Crypto 2-Day Forecast & Signals Report")
c.setFont("Helvetica", 10)
y = 700
for _, row in df.iterrows():
    text = f"{row['Coin']}: ${row['Current Price (USD)']} → ${row['Forecast (2d)']} ({row['% Change']}%) → {row['Signal']}"
    c.drawString(50, y, text)
    y -= 20
c.save()

# --- Telegram Send ---
summary = "\n".join([f"{r[0]}: {r[4]} ({r[3]}%)" for r in results])
message = f"📊 *Crypto Forecast Update*\n\n{summary}\n\n🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
telegram_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

requests.post(telegram_url, json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"})

# Send the PDF too
files = {'document': open(pdf_path, 'rb')}
requests.post(
    f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument",
    data={"chat_id": TG_CHAT_ID},
    files=files
)
