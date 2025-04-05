import requests
import json
import asyncio
import httpx
from datetime import datetime
import brotli
import gzip

url = None
headers = {
    "Host": "api.dabble.com",
    "Connection": "keep-alive",
    "Accept": "application/json",
    "User-Agent": "Dabble/113 CFNetwork/3826.400.120 Darwin/24.3.0",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Authorization": "",
    "Accept-Encoding": "gzip, deflate, br"
}
previous_odds = {}

async def main():
    global url

    # Get first NBA game
    game_url = get_first_game_id()
    if not game_url:
        print("Could not get a game URL!")
        return
    
    url = game_url
    await monitor_odds()

def get_first_game_id():
    # Get first NBA game ID of the day

    # Current NBA games endopoint
    url = "https://api.dabble.com/competitions/2acf8935-8d89-455b-bb4b-dbfba9c4ae3b/dfs-fixtures"
    try:
        response = requests.get(url, headers=headers, proxies={"http": None, "https": None})
        response.raise_for_status()
        data = response.json()

        fixtures = data.get("data")
        if fixtures:
            game_url = "https://api.dabble.com/sportfixtures/details/" + fixtures[0].get("id") + "?filter=dfs-enabled"
            game_name = fixtures[0].get("name")
            print(f"Selected game: {game_name}")
            return (game_url)
        else:
            print("No fixtures found.")
            return None

    except Exception as e:
        print(f"Error fetching match list → {e}")
        return None


async def fetch_data():
    # Fetch data from API using http2
    try:
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status() # Raise error

            # httpx auto-decodes using brotli
            text = response.text
            print("Request status:", response.status_code)
            return json.loads(text)
    except Exception as e:
        print(f"Fetch error! -> {e}")
        return None
    

def parse_odds(data):
    odds = {}

    # Map of bet {ids:names}
    id_names = {}
    selections = data.get("data").get("selections")
    for selection in selections:
        id = selection.get("id")
        bet_name = selection.get("name")

        id_names[id] = bet_name

    # Map bet {name:price} using id_names dict
    prices = data.get("data").get("prices")
    for price in prices:
        id = price.get("selectionId")
        name = id_names.get(id)
        odd_price = price.get("price")

        odds[name] = odd_price
    
    return odds


async def monitor_odds():
    # Continuosly checks for odd changes

    global previous_odds

    while True:
        data = await fetch_data()

        if data:
            current_odds = parse_odds(data)

            # Get match name
            match_name = data.get("data").get("name")

            # Loop current odds and compare prices
            for bet_name, new_price in current_odds.items():

                old_price = previous_odds.get(bet_name)

                # Check if the odd price has changed
                if old_price is not None and new_price != old_price:
                    print(f"Match: {match_name}")
                    print(f"Bet: {bet_name}")
                    print(f"Old Odds: {old_price} → New Odds: {new_price}")
                    print(f"Timestamp: {datetime.now().isoformat()}")

            # Save the current odds to compare to the next one
            previous_odds = current_odds

        # The odd prices refresh every ± 3 to 5 minutes
        await asyncio.sleep(30)



if __name__ == "__main__":
    asyncio.run(main())