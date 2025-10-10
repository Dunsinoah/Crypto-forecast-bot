import sys
import datetime
import yfinance as yf
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import telegram

coins = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Dogecoin": "DOGE-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "XRP": "XRP-USD",
    "Pepe": "PEPEUSD",  # corrected ticker
    "Sui": "SUIUSD"     # corrected ticker
}

bot_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

message_lines = ["📊 *Crypto Forecast Update*"]

for coin, symbol in coins.items():
    print(f"Fetching {coin}...")
    try:
        data = yf.download(symbol, period="90d", interval="1d")["Close"]
        if len(data) < 10:
            raise ValueError("Not enough data")

        # Prepare simple GBM model
        X = np.arange(len(data)).reshape(-1, 1)
        y = data.values
        model = GradientBoostingRegressor().fit(X, y)
        future = np.arange(len(data), len(data) + 2).reshape(-1, 1)
        forecast = model.predict(future)
        pct_change = ((forecast[-1] - y[-1]) / y[-1]) * 100
        signal = "🟢 *BUY*" if pct_change > 1 else "🔴 *SELL*" if pct_change < -1 else "⚪ *HOLD*"
        message_lines.append(f"\n💰 {coin}: {y[-1]:.2f} → {forecast[-1]:.2f} ({pct_change:.2f}%) {signal}")

    except Exception as e:
        print(f"⚠️ {coin} failed: {e}")
        message_lines.append(f"\n💰 {coin}: No data")

# Send Telegram update
bot = telegram.Bot(token=bot_token)
today = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
message = f"📅 *{today}*\n" + "\n".join(message_lines)
bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

print("✅ Telegram update sent.")
sys.exit(0)
