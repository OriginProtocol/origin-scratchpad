#! Python3
"""
    File name: treasuries.py
    Author: Jonathan Snow
    Date created: 10/21/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to determine balances of Protocol treasuries.

"""

# Imports
import requests
from modules import data

##################################################
def main():
    """
    Function to gather treasury addresses from Cryptostats.
    """

    # Get list of DAOs to process
    treasuries = get_treasuries()
    
    output_data = []
    # Process protocol treasury data
    for key in treasuries:
        output = []
        output.append(key)

        for address in treasuries[key]:
            output.append(address)
        
        output_data.append(output)


    # Dump treasury data to CSV
    output_path = "files/output"
    output_name = "treasury_addresses.csv"
    data.save(output_data, output_path, output_name,
        ["name", "ta-1", "ta-2", "ta-3", "ta-4", "ta-5", "ta-6", "ta-7", "ta-8"]
    )


##################################################
def get_treasuries():
    """
    Function to fetch a list of treasuries from
    the CryptoStats API.
    """

    url = "https://api.cryptostats.community/api/v1/treasuries/currentTreasuryUSD"

    # Get list of treasuries
    treasuries = get_data(url)["data"]

    output = {}

    # Simplify treasury data
    for treasury in treasuries:
        tid = treasury["id"]
        output[tid] = treasury["metadata"]["treasuries"]

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
    main()
