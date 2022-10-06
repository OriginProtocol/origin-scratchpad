#! Python3
"""
    File name: apyvision.py
    Author: Jonathan Snow
    Date created: 10/04/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information from APY.vision

"""

# Imports
import requests
import sys


##################################################
def process(top_tokens):
    """
    Function to fetch pool data from apy.vision and return a
    dict of tokens mapped to pool addresses.
    """
    print("Fetching data from apy.vision"  + (32 * " "))

    # Output dicts
    token_data = {}
    token_output = {}

    # General URL for pool data from APY.vision (explicitly selecting all eth DEXs tracked)
    url = "https://stats.apy.vision/api/v1/pool_search/advanced_search"\
          "?avg_period_daily_volume_usd=null&avg_period_reserve_usd=null&min_pool_age_days=7&vr=null&exchanges="\
          "balancer_eth,sushiswap_eth,uniswap_eth,oneinch_eth,balancerv2_eth,kyber_eth,curve_eth,aura_eth,aurabal_eth"\
          "&access_token=null"
    
    # Grab only the results from the query
    raw_data = get_data(url)["results"]

    # Loop over pools re†urned from apyvision
    print("Processing data from apy.vision")
    for pair in raw_data:
        pair_names = pair["name"]
        pair_list = pair_names.split("/")
        pair_count = len(pair_list)
        pool_address = pair["pool_address"]

        # Ignore pools with more than two tokens
        if pair_count == 2:
            # Loop over the pair tokens
            for raw_token in pair_list:
                # Create dict key if not exists
                if raw_token not in token_data: token_data[raw_token] = []

                # Add pool address to output list for token
                token_data[raw_token].append(pool_address)
    
    # Loop over token output data to ensure lists are unique
    for key, value in token_data.items():
        # Update key with unique values
        token_data[key] = list(set(value))
        # Check if key is not in the T500 list and remove from dict if so
        if key in top_tokens: token_output[key] = token_data[key]

    # Return relevant tokens with pool data
    return token_output


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
    test_list = ["OHM", "BAT"]
    process(test_list)
