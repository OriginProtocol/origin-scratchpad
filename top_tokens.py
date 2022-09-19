#! Python3
"""
    File name: top_tokens.py
    Author: Jonathan Snow
    Date created: 09/15/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information about Top-500 ERC20 Tokens.

    NOTE: This is a WIP script. Not validated, tested, etc.

"""

# Imports
from time import sleep, time
from modules import data
import requests
import sys

##################################################
def main():
    """
    Function to aggregate information on the top 500 tokens on Ethereum
    and grab general information about Chainlink Data Feeds, market cap,
    24-hour volume, and more.
    """

    print("\nStarting Token Analysis.")

    output = []

    # Grab list of tokens from CMC and filter by Ethereum tokens
    raw_tokens = fetch_tokens()
    eth_tokens = process_tokens(raw_tokens)[:500]

    # Fetch chainlink data feeds
    chainlink_feeds = process_chainlink_feeds()

    # Iterate over token list and prepare for data dump
    for token in eth_tokens:
        # Set up loop variables
        token_symbol = token["symbol"].upper()
        has_chainlink = False
        usd_proxy = ""
        eth_proxy = ""

        # Grab Chainlink oracle if present
        if token_symbol in chainlink_feeds:
            has_chainlink = True
            usd_proxy = chainlink_feeds[token_symbol]["USD"]
            eth_proxy = chainlink_feeds[token_symbol]["ETH"]

        # Grab protocol data from JSON file
        """
        NOTE: If not available, run /utilities/depositable_assets.py
        """
        protocol_tokens = data.load_json("files/input/depositable_assets.json")

        # Update variables if exists in dictionary else default value
        on_aave = protocol_tokens[token_symbol]["on_aave"] if token_symbol in protocol_tokens else ""
        on_compound = protocol_tokens[token_symbol]["on_compound"] if token_symbol in protocol_tokens else ""
        on_maker = protocol_tokens[token_symbol]["on_maker"] if token_symbol in protocol_tokens else ""
        on_yearn = protocol_tokens[token_symbol]["on_yearn"] if token_symbol in protocol_tokens else ""

        # Build token data list
        token_data = [
            token["name"], token["symbol"], token["platform"]["token_address"], has_chainlink, usd_proxy, eth_proxy,
            token["quotes"][0]["marketCap"], token["quotes"][0]["volume24h"], on_aave, on_compound, on_maker, on_yearn
        ]
        
        # Add to output data
        output.append(token_data)

    print("Processed " + str(len(eth_tokens)) + " tokens.")

    # Dump OGV data to CSV
    output_path = "files/output"
    output_name = "top_tokens_" + str(int(time())) + ".csv"
    data.save(output, output_path, output_name,
        ["name", "symbol", "address", "has_chainlink_feed", "usd_proxy", "eth_proxy", "market_cap_usd",
        "24h_volume", "aave", "compound", "maker", "yearn"
        ]
    )

##################################################
def fetch_tokens(limit=1000):
    """
    Function to grab a list of tokens from CoinMarketCap
    for further processing.
    """
    url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?" \
          "start=1&limit=" + str(limit) + "&sortBy=market_cap&sortType=desc" \
          "&convert=USD&cryptoType=tokens&tagType=all&audited=false"
    
    token_data = get_data(url)["data"]["cryptoCurrencyList"]
    return token_data

##################################################
def process_tokens(tokens):
    """
    Function to process a raw list of tokens, and return a
    list of all valid Ethereum tokens.
    """
    output = []
    # Loop through list and validate that the token is on Ethereum
    for token in tokens:
        # Check if ETH
        if "platform" in token and token["platform"]["id"] == 1:
            output.append(token)
    
    return output

##################################################
def process_chainlink_feeds():
    """
    Function to process the current list of all Chainlink
    Data Feeds and convert this into token pair data.
    """
    url = "https://cl-docs-addresses.web.app/addresses.json"
    chainlink_all_data = get_data(url)["ethereum-addresses"]["networks"]
    chainlink_raw_data = []
    chainlink_output = []
    output = {}

    # Grab Ethereum Mainnet data only
    for network in chainlink_all_data:
        if network["name"] == "Ethereum Mainnet":
            chainlink_raw_data.extend(network["proxies"])
            break
    
    # Process to grab only crypto feeds and add pair data
    for feed in chainlink_raw_data:
        if feed["feedCategory"] == "verified" and feed["feedType"] == "Crypto":
            # Create output dictionary for modification
            feed_output = feed
            pair = feed["pair"].split(" / ")

            # Add token and base
            feed_output["token"] = pair[0]
            feed_output["base"] = pair[1]

            chainlink_output.append(feed_output)

    # Process data into token dictionary
    """
    NOTE: Possibility of token symbol conflict. However, this doesn't 
    appear to be an issue in the top 500 tokens at this time.
    """
    for pair in chainlink_output:
        # Add token to output dictionary
        token = pair["token"].upper()

        # Add key value generic if does not exist
        if token not in output:
            output[token] = {"USD": "", "ETH": ""}

        # Check if has USD data feed
        if pair["base"] == "USD":
            output[token]["USD"] = pair["proxy"]

        # Check if has ETH data feed
        if pair["base"] == "ETH":
            output[token]["ETH"] = pair["proxy"]


    return output

##################################################
def get_data(url):
    """
    Function to fetch data from URL and return JSON output
    """
    with requests.Session() as s:
        response = s.get(url)
    return response.json()


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
