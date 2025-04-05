# 📈 Dabble Odds Monitor

**-This script monitors live betting odds for NBA games from dabble.com using their API.**

**-It fetches and tracks up to 5 games simultaneously (the number of games can be incremented depending on your region or proxy services) and notifies whenever any odds change.**

## Features

✅ Uses asyncio and httpx for efficient, concurrent requests

✅ Supports Brotli-compressed HTTP responses

✅ Handles connection and timeout errors gracefully

✅ Prints odds changes in real-time, including timestamp and bet name [Prints "..." if there are no price changes]

## How It Works

1) Fetches today's NBA fixtures

2) Selects the top NBA games of the day

3) Monitors each game’s odds every 15 seconds since the **odd prices change every 2/4 minutes** depending on the game

4) Logs the odds changes with the match name and timestamp

## Requirements

Run: **pip install httpx[http2] requests brotli**
inside your (venv).

## ⚠️ Notes
You must run behind a proxy/VPN if Dabble blocks your region.

The script mimics a mobile device using HTTP headers and HTTP/2.
<br>
![image](https://github.com/user-attachments/assets/90382727-a322-43dc-9bc2-974473d7651b)
