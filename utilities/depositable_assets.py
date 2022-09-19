#! Python3
"""
    File name: depositable_assets.py
    Author: Jonathan Snow
    Date created: 09/19/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to convert a Google Sheet CSV export into a JSON
        file for further processing.

"""

# Path update for modules
import sys
sys.path.append('..')

# Imports
from time import sleep, time
from modules import data
import requests
import math

##################################################
def main():
    """
    Function to convert a CSV of depositable assets into a
    JSON file for future use.
    """

    print("\nStarting Depositable Assets Conversion.")

    # Import data from depositable_assets CSV file
    raw_assets = data.load("../files/input/depositable_assets.csv", True)

    # Sort CSV data into dictionary
    output = process_tokens(raw_assets)

    # Export JSON file for future use
    output_path = "../files/input"
    output_name = "depositable_assets.json"
    data.save_json(output, output_path, output_name)


##################################################
def process_tokens(tokens):
    """
    Function to process a CSV list of depositable assets and
    output JSON/Dictionary object.
    """
    output = {}
    # Loop through list and validate that the token is on Ethereum
    for token in tokens:
        # Set up dictionary
        token_data = {
            "name": token[0],
            "symbol": token[1],
            "on_aave": "" if math.isnan(token[2]) else token[2],
            "on_compound": "" if math.isnan(token[3]) else token[3],
            "on_maker": "" if math.isnan(token[4]) else token[4],
            "on_yearn": "" if math.isnan(token[5]) else token[5]
        }

        # Add dictionary to output list
        output[token[1]] = token_data

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
