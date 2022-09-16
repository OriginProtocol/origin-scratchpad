#! Python3
"""
    File name: top_holders.py
    Author: Jonathan Snow
    Date created: 08/25/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to determine the top holders in a requested collection

        Notes:
        - Add in real API key to ENV
        - Alchemy API returns non-checksum addresses, shouldn't be an issue, but worth noting
        - Written for clarity, not speed. This script runs 3 operations.
"""

# Imports
import sys
import requests
from web3 import Web3
from ens import ENS

# Globals
KEY = "demo"
URL = "https://eth-mainnet.g.alchemy.com/nft/v2/" + KEY + "/getOwnersForCollection?contractAddress="

ALCHEMY = "https://eth-mainnet.alchemyapi.io/v2/" + KEY
WEB3 =  Web3(Web3.HTTPProvider(ALCHEMY))
ns = ENS.fromWeb3(WEB3)


##################################################
#
def main(address):
    """
    Function to determine the top holders of a provided collection 
    and output the relevant information to the console.
    """
    # Fetch input collection owners
    collection = get_data(URL + address + "&withTokenBalances=true")['ownerAddresses']
    print("There are " + str(len(collection)) + " unique owners in this collection.")

    # Process data on collection owners
    owner_data = process_data(collection)

    # Sort dict in descending order by values
    sorted_owners = dict(sorted(owner_data.items(), key=lambda item: item[1], reverse=True))
    
    # Pull top holder and held quantity for output
    top_holder = list(sorted_owners.keys())[0]
    top_holder_ens = get_ens_name(top_holder)
    top_holder_quantitiy = list(sorted_owners.values())[0]
    print("The top holder of Pudgy Penguins is " + top_holder_ens + " who holds " + str(top_holder_quantitiy) + " tokens.")

    # Pull top 10 holders and quantities held for output
    # Ugly code to iterate over the first 10 values in a sorted dict
    i = 1
    for holder in sorted_owners:
        each_holder = get_ens_name(holder)
        each_holder_quantity = sorted_owners[holder]
        print(each_holder + " - " + str(each_holder_quantity))

        if i < 10:
            i+=1
            continue
        else:
            break

    # Set up holder distribution dict
    hd = {
        1: 0, # 0-1
        2: 0, # 1-3
        3: 0, # 3-5
        4: 0, # 5-10
        5: 0, # 10-50
        6: 0, # 50-100
        7: 0  # >100
    }

    # Determine holder distribution
    # Reverse order as dict is already sorted DESC
    for owner in sorted_owners:
        quantity_held = sorted_owners[owner]
        # 101+
        if quantity_held >= 100:
            hd[7] += 1
        # 51-100
        elif quantity_held >= 50:
            hd[6] += 1
        # 11-50
        elif quantity_held >= 10:
            hd[5] += 1
        # 6-10
        elif quantity_held >= 5:
            hd[4] += 1
        # 4-5
        elif quantity_held >= 4:
            hd[3] += 1
        # 2-3
        elif quantity_held >= 2:
            hd[2] += 1
        # 1
        elif quantity_held == 1:
            hd[1] += 1
        else:
            continue
    
    # Ensure that no tokens were missed
    assert( (hd[1] + hd[2] + hd[3] + hd[4] + hd[5] + hd[6] + hd[7]) == len(sorted_owners) )

    print("\n" + "Token Distribution")
    print("100+: " + str(hd[7]))
    print("50-100: " + str(hd[6]))
    print("10-50: " + str(hd[5]))
    print("5-10: " + str(hd[4]))
    print("3-5: " + str(hd[3]))
    print("1-3: " + str(hd[2]))
    print("1: " + str(hd[1]))

    print("\n" + "There are " + str(hd[5] + hd[6] + hd[7]) + " High Conviction Holders that have more than 10 tokens each.")


##################################################
def process_data(input):
    """
    Function to clean up raw data and output a dict of 
    addresses along with token balance.

    input - the input data
    """
    # Setup output dict
    output = {}

    # Iterate over each owner address in list
    for wallet in input:
        address = wallet["ownerAddress"]
        balances = wallet["tokenBalances"]

        # Add to output dict
        output[address] = len(balances)
    
    return output

##################################################
def get_data(url):
    """
    Function to fetch data from URL and return JSON.
    """
    with requests.Session() as s:
        response = s.get(url)
    return response.json()

##################################################
def get_ens_name(address):
    """
    Function to lookup the ens name for an address.
    """
    ens_lookup = ns.name(address)

    if ens_lookup is None:
        return address
    else:
        return ns.name(address)


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    args = sys.argv

    if len(args) == 2:
        address = args[1]
        main(address)
    else:
        print("Collection address not entered. Please try again.")
