#! Python3
"""
    File name: bluechip.py
    Author: Jonathan Snow
    Date created: 08/20/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to determine what collection holders also hold blue chip tokens.

    Notes:
    - Add in real API key to ENV
    - Could move everything to async script, though runtime is reasonable as-is
    - Convert bluechip list to a DB call to allow the list to be updated if necessary by admin
    - Pudgy Penguins: 0xBd3531dA5CF5857e7CfAA92426877b022e612cf8
"""

# Imports
import sys
import requests

# Globals
KEY = "demo"
URL = "https://eth-mainnet.g.alchemy.com/nft/v2/" + KEY + "/getOwnersForCollection?contractAddress="

# Replace with DB call to gather current list of bluechip addresses
BLUECHIP = [
    "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb", # Cryptopunks
    "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d", # BAYC
    "0x60e4d786628fea6478f785a6d7e704777c86a7c6", # MAYC
    "0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b", # CloneX
    "0x059edd72cd353df5106d2b9cc5ab83a52287ac3a", # Chromie Squiggle
    "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e", # Doodles
    "0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7", # Meebits
    "0xed5af388653567af2f388e6224dc7c4b3241c544", # Azuki
    "0xa3aee8bce55beea1951ef834b99f3ac60d1abeeb" # Veefriends
]

'''
Can visually validate ownership:
https://opensea.io/{user_address}?search[sortBy]=LISTING_DATE
&search[collections][0]=pudgypenguins
&search[collections][1]=cryptopunks
&search[collections][2]=boredapeyachtclub
&search[collections][3]=mutant-ape-yacht-club
&search[collections][4]=clonex
&search[collections][5]=chromie-squiggle-by-snowfro
&search[collections][6]=doodles-official
&search[collections][7]=meebits
&search[collections][8]=azuki
&search[collections][9]=veefriends
'''

##################################################
def main(address):
    """
    Function to determine the ownership overlap between the provided
    collection address and bluechip collections.
    """
    # Fetch input collection owners
    collection = get_data(URL + address)['ownerAddresses']
    unique_owners = len(collection)
    print("There are " + str(unique_owners) + " unique owners in this collection.")

    # Fetch bluechip collection owners
    bluechip_owners = []
    for each in BLUECHIP:
        bluechip_data = get_data(URL + each)
        bluechip_owners.extend(bluechip_data['ownerAddresses'])

    # Isolate unique addresses from bluechips
    bluechip_unique = set(bluechip_owners)
    print("There are " + str(len(bluechip_unique)) + " unique bluechip owners.")

    # Find addresses that exist in both lists
    overlap = list(set(collection) & bluechip_unique)
    overlap_count = len(overlap)

    # Percent calculation just for output, should be done on frontend instead
    overlap_p = round((overlap_count / unique_owners) * 100, 2)

    print(str(overlap_count) + " collection owners (" + str(overlap_p) +  "%) are also blue chip holders.")


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
