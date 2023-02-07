#! Python3
"""
    File name: sewer.py
    Author: Jonathan Snow
    Date created: 01/16/2023
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to gather details about the upcoming Sewer Pass.

"""

# Imports
import requests
from modules import data
import dotenv
import os

dotenv.load_dotenv()

ALCHEMY_KEY = os.getenv("ALCHEMY_API_KEY")
URL = "https://eth-mainnet.g.alchemy.com/nft/v2/" + ALCHEMY_KEY + "/getOwnersForCollection?contractAddress="

BAYC = '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D'
MAYC = '0x60E4d786628Fea6478F785A6d7e704777c86a7c6'
BAKC = '0xba30E5F9Bb24caa003E9f2f0497Ad287FDF95623'

BLOCK = '16420600'

##################################################
def main():
    """
    Function to determine the ownership of Yuga assets
    relevant to the Sewer pass drop.
    """
    # Set up output list
    output = []

    # Set up endpoint query string
    token_string = "&withTokenBalances=true&block=" + BLOCK

    # Fetch holder data for BAYC
    bayc_raw = get_data(URL + BAYC + token_string)['ownerAddresses']
    bayc = process_data(bayc_raw)

    # Fetch holder data for MAYC
    mayc_raw = get_data(URL + MAYC + token_string)['ownerAddresses']
    mayc = process_data(mayc_raw)

    # Fetch holder data for BAKC
    bakc_raw = get_data(URL + BAKC + token_string)['ownerAddresses']
    bakc = process_data(bakc_raw)

    # Get list of unique holder addresses
    addresses = []
    addresses.extend(bayc.keys())
    addresses.extend(mayc.keys())
    addresses.extend(bakc.keys())
    holders = list(set(addresses))

    # Loop over unique holders to generate output list
    for holder in holders:
        holder_bayc = get_balance(holder, bayc)
        holder_mayc = get_balance(holder, mayc)
        holder_bakc = get_balance(holder, bakc)

        # Set balance variables
        balance_bayc = holder_bayc
        balance_mayc = holder_mayc
        balance_bakc = holder_bakc

        # Determine holder redemption
        # TIER 4 (BAYC + BAKC)
        if balance_bayc > 0 and balance_bakc > 0:
            t4p = min(balance_bayc, balance_bakc)
            balance_bayc -= t4p
            balance_bakc -= t4p
        else:
            t4p = 0

        # TIER 3 (BAYC)
        if balance_bayc > 0:
            t3p = balance_bayc
            balance_bayc -= t3p
        else:
            t3p = 0

        # TIER 2 (MAYC + BAKC)
        if balance_mayc > 0 and balance_bakc > 0:
            t2p = min(balance_mayc, balance_bakc)
            balance_mayc -= t2p
            balance_bakc -= t2p
        else:
            t2p = 0

        # TIER 1 (MAYC)
        if balance_mayc > 0:
            t1p = balance_mayc
            balance_mayc -= t1p
        else:
            t1p = 0

        holder_output = [holder, holder_bayc, holder_mayc, holder_bakc, t4p, t3p, t2p, t1p]
        output.append(holder_output)

        print(holder + ": " + str(holder_bayc) + ", " + str(holder_mayc) + ", " + str(holder_bakc))

    # Dump balance data to CSV
    output_path = "files/output"
    output_name = "yuga_balances_" + str(BLOCK) + "-2.csv"
    data.save(output, output_path, output_name, ["address", "BAYC", "MAYC", "BAKC", "T4", "T3", "T2", "T1"])


##################################################
def get_data(url):
    """
    Function to fetch data from URL and return JSON
    """
    with requests.Session() as s:
        response = s.get(url)
    return response.json()

##################################################
def process_data(input):
    output = {}

    # Iterate over ownership data by address
    for owner in input:
        address = owner["ownerAddress"]
        balance = len(owner["tokenBalances"])
        output[address] = balance
        # print(address + ": " + str(balance))
    
    return output

##################################################
def get_balance(address, addresses):
    # Check if address is in the list else 0
    if address in addresses.keys():
        return addresses[address]
    else:
        return 0

##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
