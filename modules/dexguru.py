#! Python3
"""
    File name: dexguru.py
    Author: Jonathan Snow
    Date created: 10/03/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information from dex.guru

        NOTE: The async processor should eventually be turned into a generic module.
        For the time being, a number of files might (definitely will) share similar code.

"""

import json
import asyncio
import aiohttp

##################################################
def scrape_async(addr):
    """
    Function to asynchronously scrape token data from dexguru from
    as provided list of contract addresses.
    """
    output = asyncio.run(scrape(addr))
    return output

##################################################
async def scrape(addresses):
    """
    Function to start async routine and return clean data.
    """
    # Prepare output dict
    token_data = {}
    for address in addresses:
        token_data[address] = {}

    # Start async scrape process
    data = await scrape_helper(addresses)

    # Iterate over data returned from async process
    for token in data:
        try:
            token_json = json.loads(str(token))
            token_data[token_json["address"]] = token_json["data"]
        except Exception as e:
            print("JSON Error: " + str(e) + " : " + str(token))

    return token_data


##################################################
async def scrape_helper(addresses):
    """
    Function to create a ClientSession and to pass along
    to the data fetching function.
    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        tokens = await fetch_data(client, addresses)
    return tokens


##################################################
async def fetch_data(client, addresses):
    """
    Function to wrap the get_data coroutine into a task
    for execution asynchronously.
    """
    tasks = []
    for i in range(0, len(addresses)):
        task = asyncio.create_task(get_data(client, addresses[i]))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


##################################################
async def get_data(client, address):
    """
    Function to generate the urls to scrape and to package
    the response into an object for future processing.
    """
    print("Scraping Address: " + str(address), end='\r', flush=True)
    url = "https://api.dex.guru/v3/tokens/search/" + address + "?network=eth"

    async with client.get(url) as response:
        try:
            assert response.status == 200
            data = await response.text()
            return '{"address": "' + str(address) + '", "data": ' + data +'}'
        except AssertionError:
            print("Error Processing Address (dex.guru): " + str(address) + " with error code " + str(response.status))
            print(url)
            return '{"address": "' + str(address) + '", "data": "none"}'


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    test_addresses = [
        "0x0d8775f648430679a709e98d2b0cb6250d2887ef",
        "0x8E870D67F660D95d5be530380D0eC0bd388289E1",
        "0x674C6Ad92Fd080e4004b2312b45f796a192D27a0",
        "0xE66747a101bFF2dBA3697199DCcE5b743b454759",
        "0x4d224452801ACEd8B2F0aebE155379bb5D594381"
    ]
    scrape_async(test_addresses)
