#! Python3
"""
    File name: holders.py
    Author: Jonathan Snow
    Date created: 10/04/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information from holders.at.
        This is just a simple API endpoint to pull current owners for a
        provided contract.

        Async code caused some issues with the site, sorry. Could be fixed by
        updating concurrent connections, timeout, or retry on failure...
        Not worth the time to fix, slow takes 3-4 minutes.

"""

import json
import asyncio
import aiohttp
import requests
import sys

BURN = "0x0000000000000000000000000000000000000000"

##################################################
def scrape_slow(addr, block):
    """
    Function to scrape the data, but slower.
    """
    print("Processing Holder Data (slow-mode):")

    # Set up some stuff
    output = {}
    session = requests.Session()

    # Terminal output stuff
    i=1
    l=len(addr)

    # Loop over pool addresses
    for pool in addr:
        print("Processing: " + str(i) + " / " + str(l) + "          ", end='\r')
        url = "https://api.holders.at/holders?network=ethereum&collection=" + pool + "&block=" + str(block)
        response = session.get(url)
        lp_list = response.json()

        # Remove burn address if present
        if BURN in lp_list: lp_list.remove(BURN)
        
        # Add LP count to output dict
        output[pool] = len(lp_list)
        i+=1

    return output



##################################################
def scrape_async(addr, block):
    """
    Function to asynchronously scrape token data from holders.at from
    the provided list of contract addresses and block number.
    """
    print("Processing Holder Data (fast-mode):")
    output = asyncio.run(scrape(addr, block))
    return output


##################################################
async def scrape(addresses, block):
    """
    Function to start async routine and return clean data.
    """
    # Prepare output dict
    token_data = {}
    for address in addresses:
        token_data[address] = {}

    # Start async scrape process
    data = await scrape_helper(addresses, block)

    # Iterate over data returned from async process
    for token in data:
        try:
            token_json = json.loads(str(token))
            token_data[token_json["address"]] = token_json["data"]
        except Exception as e:
            print("JSON Error: " + str(e) + " : " + str(token))

    return token_data


##################################################
async def scrape_helper(addresses, block):
    """
    Function to create a ClientSession and to pass along
    to the data fetching function.
    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        tokens = await fetch_data(client, addresses, block)
    return tokens


##################################################
async def fetch_data(client, addresses, block):
    """
    Function to wrap the get_data coroutine into a task
    for execution asynchronously.
    """
    tasks = []
    for i in range(0, len(addresses)):
        task = asyncio.create_task(get_data(client, addresses[i], block))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


##################################################
async def get_data(client, address, block):
    """
    Function to generate the urls to scrape and to package
    the response into an object for future processing.
    """
    print("Scraping Address: " + str(address), end='\r', flush=True)
    url = "https://api.holders.at/holders?network=ethereum&collection=" + address + "&block=" + str(block)

    async with client.get(url) as response:
        try:
            assert response.status == 200
            data = await response.text()
            return '{"address": "' + str(address) + '", "data": ' + data +'}'
        except AssertionError:
            print("Error Processing Address (holders): " + str(address) + " with error code " + str(response.status))
            return '{"address": "' + str(address) + '", "data": "none"}'


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    test_addresses = [
        "0x88172e5d79fe75c7aed1453e89ff5d741cfa4ca7",
        "0x4632ac4a94b57573f6b0297229fc8d54046f9be4",
        "0x9c656767097a224eebd675752769f992052ff060",
        "0x47cc251423dfdeb0b49047e0a219ea08ab9b9407",
        "0xb594855535a10b68c06b3ee03d0d5ec030a68d53"
    ]
    scrape_slow(test_addresses, 15682642)
