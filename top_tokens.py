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
from time import time, sleep
from modules import data, eth, db
import requests
import sys

DEBUG = False

##################################################
def main():
    """
    Function to aggregate information on the top 500 tokens on Ethereum
    and grab general information about Chainlink Data Feeds, market cap,
    24-hour volume, CEX availability, and more.
    """

    print("\nStarting Token Analysis.")

    output = []
    i = 1

    # Grab list of tokens from CMC and filter by Ethereum tokens
    raw_tokens = fetch_tokens()
    eth_tokens = process_tokens(raw_tokens)[:500]

    # Fetch chainlink data feeds
    chainlink_feeds = process_chainlink_feeds()

    # Fetch current exchange pairs
    exchange_tokens = get_exchange_tokens()

    # Iterate over token list and prepare for data dump
    for token in eth_tokens:
        print("\rProcessing contract " + str(i) + " / " + str(len(eth_tokens)) + "          ", end="", flush=True)

        # Set up loop variables
        address = eth.get_checksum(token["platform"]["token_address"])
        token_symbol = token["symbol"].upper()
        has_chainlink = False
        usd_proxy = ""
        eth_proxy = ""

        # Fetch contract data from DB else process
        contract_data = process_contract(address)

        # Check if contract is verified on Etherscan
        etherscan_verified = True if contract_data[1] == 1 else False

        # Grab Chainlink oracle if present
        if token_symbol in chainlink_feeds:
            has_chainlink = True
            usd_proxy = chainlink_feeds[token_symbol]["USD"]
            eth_proxy = chainlink_feeds[token_symbol]["ETH"]

        # Grab protocol data from JSON file
        """
        If not available, run /utilities/depositable_assets.py
        """
        protocol_tokens = data.load_json("files/input/depositable_assets.json")

        # Update variables if exists in dictionary else default value
        on_aave = protocol_tokens[token_symbol]["on_aave"] if token_symbol in protocol_tokens else ""
        on_compound = protocol_tokens[token_symbol]["on_compound"] if token_symbol in protocol_tokens else ""
        on_maker = protocol_tokens[token_symbol]["on_maker"] if token_symbol in protocol_tokens else ""
        on_yearn = protocol_tokens[token_symbol]["on_yearn"] if token_symbol in protocol_tokens else ""

        # Get count of exchanges token is listed on else 0
        exchange_count = 0 if token_symbol not in exchange_tokens else len(exchange_tokens[token_symbol]["exchanges"])

        # Check if eligible for Chainlink Data Feed
        volume_24h = token["quotes"][0]["volume24h"]
        chainlink_eligible = exchange_count >= 3 and volume_24h > 3000000


        # DEBUG code used to validate the exchange listings for a specific hardcoded token symbol
        if DEBUG:
            if token_symbol == "USDT":
                print(exchange_tokens[token_symbol]["exchanges"])

        # FUTURE: Get DEX details/data

        # Build token data list
        token_data = [
            token["name"], token["symbol"], address, etherscan_verified, chainlink_eligible, has_chainlink,
            usd_proxy, eth_proxy, token["quotes"][0]["marketCap"], volume_24h, exchange_count, 
            on_aave, on_compound, on_maker, on_yearn
        ]

        # Add to output data
        output.append(token_data)

        # Increment counter
        i+=1

    print("\nProcessed " + str(len(eth_tokens)) + " tokens.")

    # Dump token data to CSV
    output_path = "files/output"
    output_name = "top_tokens_" + str(int(time())) + ".csv"
    data.save(output, output_path, output_name,
        ["name", "symbol", "address", "etherscan_verified", "chainlink_eligible", "has_chainlink_feed", "usd_proxy", 
        "eth_proxy", "market_cap_usd", "24h_volume", "cex_count", "aave", "compound", "maker", "yearn"
        ]
    )

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

    """
    There is a possibility of token symbol key conflict. However, this
    doesn't appear to be an issue in the top 500 tokens at this time.
    """
    # Process data into token dictionary
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
def process_contract(address):
    """
    Function to take a contract address and query the
    DB for details or trigger a processing to add the 
    contract address to the DB.
    """
    contract_details = db.get_contract(address)

    # Check if user exists in the DB
    if contract_details is None:

        # Check if contract is verified on Etherscan
        is_verified = eth.is_contract_verified(address)

        # Pull contract deploy date
        deploy_date = eth.get_contract_deploy_date(address)

        # Add contract to the DB
        db.add_contract(address, is_verified, deploy_date)

        # Pull standardized data from DB
        contract_details = db.get_contract(address)

    return contract_details


##################################################
def get_exchange_tokens():
    """
    Function to fetch a list of all top exchange pairs.
    """
    output = {}
    exchange_data = []
    exchanges = [
        "binance", "kraken", "ftx", "kucoin", "bitfinex", "gemini", "bybit", "coinbase-exchange",
        "gate-io", "huobi-global", "bitstamp", "okx"
    ]

    # Fetch raw data for token pairs on provided exchange slugs
    for exchange in exchanges:
        data = get_exchange_pairs(exchange)
        exchange_data.extend(data)
    
    # Clean up data to make it easier to query by token symbol
    for pair in exchange_data:

        # Create list of the two possible pair symbols
        base_data = [pair["baseSymbol"], pair["quoteSymbol"]]

        # Loop over two symbols (small loop to be DRY)
        for base in base_data:

            # Check if base in output list else setup
            if base not in output:
                output[base] = {}
                output[base]["data"] = []
                output[base]["exchanges"] = []

            # Add data to pair dict
            output[base]["data"].append(pair)

            # Check if exchange in list already
            if pair["exchangeSlug"] not in output[base]["exchanges"]:
                output[base]["exchanges"].append(pair["exchangeSlug"])

    return output

##################################################
def get_exchange_pairs(exchange):
    """
    Function to fetch a list of all exchange pairs for
    a provided exchange slug. Default page size is 500.
    """
    output = []
    start = 1
    while True:
        # Build URL and fetch data from CMC
        url = "https://api.coinmarketcap.com/data-api/v3/exchange/market-pairs/latest?slug=" \
            + exchange + "&category=spot&start=" + str(start) + "&limit=500"
        data = get_data(url)
        pairs = data["data"]["marketPairs"]

        # Break loop if no pairs are returned
        if len(pairs) == 0: break

        # Add pairs to output list
        output.extend(pairs)

        # Increment start value
        start += 500
    
    return output


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
