#! Python3
"""
    File name: yearn.py
    Author: Jonathan Snow
    Date created: 09/19/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information about available Yearn Vaults.

"""

# Imports
from time import sleep, time
from modules import data
import requests
import sys

##################################################
def main():
    """
    Function to export a CSV containing the current yearn vaults.
    """

    print("\nStarting Yearn Vault Analysis.")

    # Grab list of tokens from Yearn and process to find supported vaults
    url = "https://cache.yearn.finance/v1/chains/1/tokens/supported"
    raw_tokens = get_data(url)
    supported_tokens = process_tokens(raw_tokens)

    print(supported_tokens)
    print(len(supported_tokens))


    # Dump OGV data to CSV
    output_path = "files/output"
    output_name = "yearn_vaults_" + str(int(time())) + ".csv"
    data.save(supported_tokens, output_path, output_name,
        ["name", "symbol", "address"]
    )


##################################################
def process_tokens(tokens):
    """
    Function to process a raw list of vaults and return
    a simplified list for export to CSV
    """
    output = []
    # Loop through list and validate that the token is on Ethereum
    for token in tokens:
        # Check if ETH
        if "supported" in token:
            if "vaults" in token["supported"] and token["supported"]["vaults"] == True:
                output.append([
                    token["name"],
                    token["symbol"],
                    token["address"]
                ])
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
# Runtime Entry Point
if __name__ == "__main__":
    main()
