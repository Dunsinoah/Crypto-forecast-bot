name: Daily Crypto Forecast

on:
  schedule:
    - cron: "0 6 * * *"  # 6 AM UTC (7 AM Nigeria)
  workflow_dispatch:     # allows manual run

jobs:
  run-forecast:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install pycoingecko pandas numpy reportlab requests

      - name: Run bot
        env:
          TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}
          TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}
        run: python crypto_telegram_report.py
