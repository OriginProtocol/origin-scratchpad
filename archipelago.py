#! Python3
"""
    File name: archipelago.py
    Author: Jonathan Snow
    Date created: 12/09/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information about the artblocks
        exchange Archipelago (https://archipelago.art/)

"""

# Imports
from time import sleep, time
from modules import eth
from termcolor import colored

DEBUG = False
PROCESSING = False

# Globals
START_BLOCK = 14997767 # contract deployment block (reduces block scanning)
LATEST_BLOCK = eth.get_latest_block()

# Load contracts
ADDRESS = "0x555598409fE9A72f0A5e423245c34555F6445555"
ROYALTY = "0x1fC12C9f68A6B0633Ba5897A40A8e61ed9274dC9"
ARCH = eth.get_contract(ADDRESS, eth.get_contract_abi(ADDRESS))

##################################################
def main():
    """
    Function to do a bunch of stuff. Not optimized and no tests.
    """
    print("\nStarting Archipelago analysis.")

    # Fetch all Transfer logs for the OGN contract since deployment
    # Due to periods of high volume, need to set block range to low value (2,000)
    royalty_logs = get_logs(ARCH, START_BLOCK, LATEST_BLOCK, 500000)

    royalty_payments = []
    # royalty_currencies = []
    royalty_amount = 0

    for log in royalty_logs:
        recipient = log["args"]["recipient"]

        if recipient == ROYALTY:
            royalty_payments.append(log["logIndex"]) # Append random data to determine quantity
            # royalty_currencies.append(log["args"]["currency"]) # Only WETH
            tx_royalty_amount = log["args"]["amount"] / 1e18
            royalty_amount += tx_royalty_amount


    
    print("There were " + str(len(royalty_payments)) + " royalty payments received.")
    #print("The number of royalty currencies is " + str(len(set(royalty_currencies))))
    print("The total royalties earned was " + str(royalty_amount) + " WETH.")


##################################################
def get_logs(contract, from_block, to_block, gap=1000000):
    """
    Function to get all transfer logs for a provided contract.
    NOTE: This can run slowly depending on when the contract was
    deployed and the block gap may need to be adjusted depending
    on the activity within the collection. Designed for a specific
    objective and is not efficient for all collections. Limited to
    10k logs with > 2000 block range, unlimited logs with block range
    that is <= 2,000.
    """
    s_time = time()
    output = []

    # Limit to how many events we can call at once, break calls into smaller chunks
    start_block = from_block
    end_block = to_block if (to_block - from_block) <= gap else (start_block + gap)

    while True:
        # Output processing progress
        print("Processing: " + str(start_block) + " / " + str(to_block) + "          ", end='\r')

        # Grab events from a range of blocks
        royalty_filter = contract.events.RoyaltyPayment.createFilter(fromBlock=start_block, toBlock=end_block)
        royalty_entries = royalty_filter.get_all_entries()

        # Log
        if DEBUG: print("Fetched: " + str(start_block) + " to " + str(end_block))

        # Add events to the output list
        output.extend(royalty_entries)

        # Break loop if end_block equals the desired to_block
        if end_block == to_block: break

        # Adjust start_block to be the previous end_block
        start_block = end_block

        # Adjust end_block to the to_block if adding the gap takes us over the 
        # desired to_block, otherwise, add the gap to the new start_block
        end_block = to_block if (start_block + gap) > to_block else (start_block + gap)

    e_time = time()
    print(colored("\nRetrieved Events in " + str(round(e_time-s_time,2)) + "s", 'green'))
    return output



##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
