import requests
import json
import asyncio
import httpx
from datetime import datetime
import brotli
import gzip

headers = {
    "Host": "api.dabble.com",
    "Connection": "keep-alive",
    "Accept": "application/json",
    "User-Agent": "Dabble/113 CFNetwork/3826.400.120 Darwin/24.3.0",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Authorization": "",
    "Accept-Encoding": "gzip, deflate, br"
}

async def main():

    # Get NBA game ids
    game_urls = get_game_ids()
    if not game_urls:
        print("Could not get game URLs!")
        return
    
    # Append and execute tasks
    tasks = []
    print("Monitoring the following games: ")
    for game_name, game_url in game_urls.items():
        print(f"    -{game_name}")
        tasks.append(asyncio.create_task(monitor_odds(game_name, game_url)))

    await asyncio.gather(*tasks)

def get_game_ids():
    # Get first NBA game ID of the day

    # Current NBA games endopoint
    url = "https://api.dabble.com/competitions/2acf8935-8d89-455b-bb4b-dbfba9c4ae3b/dfs-fixtures"
    try:
        response = requests.get(url, headers=headers, proxies={"http": None, "https": None})
        response.raise_for_status()
        data = response.json()

        fixtures = data.get("data")
        if fixtures:
            game_urls = {}
            MAX_GAMES = 3
            for game in range(min(MAX_GAMES, len(fixtures))):
                game_url = "https://api.dabble.com/sportfixtures/details/" + fixtures[game].get("id") + "?filter=dfs-enabled"
                game_name = fixtures[game].get("name")
                game_urls[game_name] = game_url
            return game_urls
        else:
            print("No fixtures found.")
            return None

    except Exception as e:
        print(f"Error fetching match list → {e}")
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


async def monitor_odds(game_name, game_url):
    # Continuosly checks for odd changes

    previous_odds = {}

    async def fetch_data():
        # Fetch data from API using http2
        try:
            async with httpx.AsyncClient(http2=True, verify=False) as client:
                response = await client.get(game_url, headers=headers)
                response.raise_for_status() # Raise error

                # httpx auto-decodes using brotli
                text = response.text
                print("...")
                return json.loads(text)
        except Exception as e:
            print(f"Fetch error! -> {e}")
            return None

    while True:
        data = await fetch_data()

        if data:
            current_odds = parse_odds(data)

            # Loop current odds and compare prices
            for bet_name, new_price in current_odds.items():

                old_price = previous_odds.get(bet_name)

                # Check if the odd price has changed
                if old_price is not None and new_price != old_price:
                    print(f"Match: {game_name}")
                    print(f"Bet: {bet_name}")
                    print(f"Old Odds: {old_price} → New Odds: {new_price}")
                    print(f"Timestamp: {datetime.now().isoformat()}")

            # Save the current odds to compare to the next one
            previous_odds = current_odds

        # The odd prices refresh every ± 3 to 5 minutes
        await asyncio.sleep(30)



if __name__ == "__main__":
    asyncio.run(main())