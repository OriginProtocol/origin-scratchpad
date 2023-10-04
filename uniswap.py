#! Python3
"""
    File name: uniswap.py
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to check the list of
        whitelisted tokens on Uniswap.

"""

from time import sleep, time
from modules import data
import requests
import sys

DEBUG = False
PROCESSING = False

# Globals
URL = "https://gateway.ipfs.io/ipns/tokens.uniswap.org"

##################################################
def main():
    """
    Function to do a bunch of stuff. Not optimized and no tests.
    """
    print("\nStarting Uniswap analysis.")

    # Set up output variables
    uniswap_tokens = []
    output = []

    # Grab list of tokens from CMC and filter by Ethereum tokens
    raw_tokens = fetch_tokens()
    eth_tokens = process_tokens(raw_tokens)[:500]

    # Grab the list of whitelisted tokens
    tokens = get_data(URL)

    # Process tokens if response exists
    if tokens.get("tokens") is not None:

        for token in tokens["tokens"]:
            if token["chainId"] == 1:
                uniswap_tokens.append(token["address"])
    
    # Process CMC Top 100
    for listing in eth_tokens:
        if listing["platform"]["id"] == 1:
            if listing["platform"]["token_address"] in uniswap_tokens:
                # Grab token data
                token_name = listing["name"]
                token_symbol = listing["symbol"]
                token_address = listing["platform"]["token_address"]
                token_market_cap = listing["quotes"][0]["marketCap"]

                # Add to output list
                output.append([token_name, token_symbol, token_market_cap, token_address])

    # Dump token data to CSV
    output_path = "files/output"
    output_name = "uniswap_" + str(int(time())) + ".csv"
    data.save(output, output_path, output_name,["name", "symbol", "market_cap", "address"])


##################################################
def fetch_tokens(limit=1000):
    """
    Function to grab a list of tokens from CoinMarketCap
    for further processing. Default page size is 1000.
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
def get_data(url):
    """
    Function to fetch data from URL and return JSON output.
    """
    with requests.Session() as s:
        response = s.get(url)
    return response.json()

##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
