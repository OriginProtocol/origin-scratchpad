#! Python3
"""
    File name: ogv_balances.py
    Author: Jonathan Snow
    Date created: 09/16/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information about OGV owners
        and dump the data to CSV.
    Notes:
        - Look at Curve tokens in future [0x87650D7bbfC3A9F10587d7778206671719d9910D]

"""

# Imports
from time import sleep, time
from modules import data, eth, db
from termcolor import colored

# Globals
START_BLOCK = 14439231 # OGV deployment block (reduces block scanning)
LATEST_BLOCK = eth.get_latest_block()
#LATEST_BLOCK = 15540942
OGV = eth.get_contract("0x9c354503C38481a7A7a51629142963F98eCC12D0")


##################################################
def main():
    """
    Function to pull some basic data on OGV users.
    """
    print("\nStarting OGV analysis.")

    # Fetch all Transfer logs for the OGV contract since deployment
    ogv_transfer_logs = eth.get_transfer_logs(OGV, START_BLOCK, LATEST_BLOCK, 50000)

    # Process transfer logs into list of dictionary objects
    transfer_logs = process_logs(ogv_transfer_logs)

    # Process normalized logs into dictionary of block interaction by user
    user_interaction = process_user_logs(transfer_logs)

    # Generate list of users to process from Transfer logs and remove burn address
    users = list(user_interaction.keys())
    users.remove("0x0000000000000000000000000000000000000000")


    # Iterate over list of addresses and pull data on user
    output = []
    i = 1
    users_count = len(users)
    for user in users:
        #print("Processing: " + str(start_block) + " / " + str(to_block) + "          ", end='\r')
        print("\rProcessing user " + str(i) + " / " + str(users_count) + "          ", end="", flush=True)

        # Make sure user address is in proper checksum format
        user = eth.get_checksum(user)

        # Fetch user details from DB or trigger a processing
        user_details = process_user(user)

        # Pull user ENS if present
        user_ens = user_details[1]

        # Get current OGV Token Balance
        ogv_balance = round(eth.get_token_balance(OGV, user, LATEST_BLOCK) / 1e18, 2)

        # Get the current ETH balance for the user
        eth_balance = float(round(eth.wei_to_ether(eth.get_balance(user, LATEST_BLOCK)), 2))

        # Get the number of OGV Transfers for user
        num_ogv_logs = len(user_interaction[user])

        # Check if the address is a contract
        is_contract = user_details[2]

        # Add data to output list
        output.append([
            user, user_ens, is_contract, ogv_balance, eth_balance, num_ogv_logs
        ])

        i+=1

    # Dump OGV data to CSV
    output_path = "files/output"
    output_name = "ogv_" + str(LATEST_BLOCK) + ".csv"
    data.save(output, output_path, output_name,
        ["address", "ens", "is_contract",  "ogv_balance", "eth_balance", "number_ogv_events"]
    )

##################################################
def process_logs(logs):
    """
    Function to take a list of raw events and process into a list
    of standardized dictionary objects for further processing.
    """
    print("\nPreparing to process " + str(len(logs)) + " events.")
    s_time = time()

    # Iterate over logs and organize into a list of dictionary objects
    output = []
    for log in logs:
        data = {
            'block': log["blockNumber"],
            'transaction': log["transactionHash"].hex(),
            'transaction_index': log["transactionIndex"],
            'log_index': log["logIndex"],
            'from': log.args["from"],
            'to': log.args["to"],
            'value': log.args["value"] / 1e18
        }
        output.append(data)

    e_time = time()
    print(colored("Processed events in " + str(round(e_time-s_time,2)) + "s\n",'green'))

    return output

##################################################
def process_user_logs(logs):
    """
    Function to process user logs into a dictionary
    of addresses mapped to an array of the blocks
    that address has interacted with.
    """
    output = {}

    for log in logs:
        from_address = log["from"]
        to_address = log["to"]
        block = log["block"]

        # Add from_address block to key
        if from_address in output.keys():
            output[from_address] += [block]
        else:
            output[from_address] = [block]

        # Add to_address block to key
        if to_address in output.keys():
            output[to_address] += [block]
        else:
            output[to_address] = [block]

    return output

##################################################
def process_user(address):
    """
    Function to take an address and query the DB for details
    or trigger a processing to add the address to DB.
    """
    user_details = db.get_user(address)

    # Check if user exists in the DB
    if user_details is None:

        # Check for ENS name for address
        ens_name = eth.get_ens_name(address)

        # Check if address is a contract
        is_contract = eth.is_contract(address)

        # Pull first activity date based on whether address is a contract
        if is_contract:
            first_activity = eth.get_contract_deploy_date(address)
        else:
            first_activity = eth.get_first_transaction(address)

        # Add user to the DB
        db.add_user(address, ens_name, is_contract, first_activity)

        # Pull standardized data from DB
        user_details = db.get_user(address)

    return user_details

##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
