#! Python3
"""
    File name: minters.py
    Author: Jonathan Snow
    Date created: 09/07/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to generate a list of all addresses that
        minted an NFT from a provided contract address.
"""

# Imports
from time import sleep, time
from modules import eth, config, data
from termcolor import colored
import sys

DEBUG = False

# Load latest block and create contract object with generic ABI
BLOCK = eth.get_latest_block()
ABI = config.load("modules/abi/origin_721.json")


##################################################
def main(address):
    """
    Function to pull all Transfer events from a contract and process
    these events to determine which addresses minted an NFT.
    """

    print("\nStarting Contract Minter Analysis.")

    # Grab deployment block from Etherscan to simplify processing
    start_block = eth.get_contract_deploy_date(address, True)

    # Create contract object using Origin ERC721 ABI
    contract = eth.get_contract(address, ABI)

    # Get all transfer logs for the provided contract with a 50k block interval
    transfers = eth.get_transfer_logs(contract, start_block, BLOCK, 1000)

    # Find all unique user addresses that received an NFT from burn address
    users = process_events(transfers)

    # Save list as a CSV
    output_path = "files/output"
    output_name = address + "_" + str(BLOCK) + ".csv"
    data.save(users, output_path, output_name, ["Address"])

##################################################
def process_events(logs):
    """
    Function to take a list of raw events and process into a list
    of addresses for further processing.
    """

    print("Preparing to process " + str(len(logs)) + " events.")
    s_time = time()

    # Iterate over logs and organize into a list of users
    output = []
    for log in logs:
        from_address = log.args["from"]
        # If sender is burn address, Transfer is a mint
        if from_address == "0x0000000000000000000000000000000000000000":
            output.append(log.args["to"])

    e_time = time()
    print(colored("Processed events in " + str(round(e_time-s_time,2)) + "s",'green'))

    output = list(set(output))
    print("Found " + str(len(output)) + " users.")

    return output


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    args = sys.argv

    if len(args) == 2:
        address = args[1]
        main(address)
    else:
        print("Collection address not entered. Please try again.")
