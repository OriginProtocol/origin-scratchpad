#! Python3
"""
    File name: notable_holders.py
    Author: Jonathan Snow
    Date created: 08/20/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to determine what notable holders own items in a requested collection

        Notes:
        - Add in real API key to ENV
        - Alchemy API returns non-checksum addresses, shouldn't be an issue, but worth noting
        - Notable wallets list should be moved to DB so can be updated in admin frontend
"""

# Imports
import sys
import requests

# Globals
KEY = "demo"
URL = "https://eth-mainnet.g.alchemy.com/nft/v2/" + KEY + "/getOwnersForCollection?contractAddress="

# Dict of 'notable' holders to check on
WALLETS = {
    "0xd387a6e4e84a6c86bd90c158c6028a58cc8ac459" : "Pranksy",
    "0x4a7c6899cdcb379e284fbfd045462e751da4c7ce" : "Alex Svanevik",
    "0x787349b0c7d3bdf2583f2ba586b4990074593be1" : "Fedor Holz",
    "0x0f0eae91990140c560d4156db4f00c854dc8f09e" : "VincentVanDough",
    "0xc5f59709974262c4afacc5386287820bdbc7eb3a" : "Farokh",
    "0x1da5331994e781ab0e2af9f85bfce2037a514170": "Seedphrase"
}


##################################################
#
def main(address):
    """
    Function to determine the notable holders (external) from
    a provided collection address and output results to the console.
    """
    # Fetch input collection owners
    collection = get_data(URL + address + "&withTokenBalances=true")['ownerAddresses']
    print("There are " + str(len(collection)) + " unique owners in this collection.")

    # Process data to compare to notable addresses list
    owner_data = process_data(collection)

    # Iterate over notable addresses list to determine overlap
    for address in WALLETS:
        # Check if address exists in owner_data
        if address in owner_data:
            print(WALLETS[address] + " owns " + str(owner_data[address]["balance"]) + 
                  " Token" + ("s" if owner_data[address]["balance"] > 1 else "") + "!"
            )


##################################################
def process_data(input):
    """
    Function to clean up raw data. There are some unnecessary manipulation in
    this function. Just need to iterate over data input and map address to
    balance (similar to top_holders process_data function).
    """
    # Setup output dict
    output = {}

    # Iterate over each owner address in list
    for wallet in input:
        address = wallet["ownerAddress"]
        balances = wallet["tokenBalances"]
        tokens = []

        # loop over owned tokens to produce clean list of token ids
        for token in balances:
            # Grab tokenId, ignore balance (ERC721), convert hex to int
            token_str = token['tokenId'][-4:]
            token_id = int(token_str, base=16)
            tokens.append(token_id)

        # Add to output dict
        output[address] = {
            'balance': len(balances),
            'tokens': tokens
        }
    
    return output

##################################################
def get_data(url):
    """
    Function to fetch data from URL and return JSON
    """
    with requests.Session() as s:
        response = s.get(url)
    return response.json()


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    args = sys.argv

    if len(args) == 2:
        address = args[1]
        main(address)
    else:
        print("Collection address not entered. Please try again.")
