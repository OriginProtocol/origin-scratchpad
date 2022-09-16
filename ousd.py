#! Python3
"""
    File name: ousd.py
    Author: Jonathan Snow
    Date created: 08/27/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull information about OUSD owners
        and dump the data to CSV.
    Notes:
        - Look at Curve tokens in future [0x87650D7bbfC3A9F10587d7778206671719d9910D]

"""

# Imports
from time import sleep, time
from modules import data, eth, db
from termcolor import colored

DEBUG = False

# Globals
START_BLOCK = 10884563 # OUSD deployment block (reduces block scanning)
LATEST_BLOCK = eth.get_latest_block()
OUSD = eth.get_contract("0x2A8e1E676Ec238d8A992307B495b45B3fEAa5e86")
USDT = eth.get_contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")
USDC = eth.get_contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
DAI  = eth.get_contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")

TEST = [
    "0x3f06440e317c3600873Ab24868B51697EB2D2eD5",
    "0x9C94df9d594BA1eb94430C006c269C314B1A8281"
    ]

##################################################
def main():
    """
    Function to do a bunch of stuff. Not optimized and no tests.
    Takes ~ 40-minutes to run once DB is populated.
    """
    print("\nStarting OUSD analysis.")

    # Fetch all Transfer logs for the OUSD contract since deployment
    ousd_transfer_logs = eth.get_transfer_logs(OUSD, START_BLOCK, LATEST_BLOCK)

    # Process transfer logs into list of dictionary objects
    transfer_logs = process_logs(ousd_transfer_logs)

    # Process normalized logs into dictionary of block interaction by user
    user_interaction = process_user_logs(transfer_logs)

    # Generate list of users to process from Transfer logs and remove burn address
    users = list(user_interaction.keys())
    users.remove("0x0000000000000000000000000000000000000000")

    # Use dummy list if debug flag is True
    if DEBUG: users = TEST

    """
    OFFLOAD TO SEPARATE FUNCTION? process_users()
    Could pass user_interaction, create users list and return output list
    """

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

        # Get current token balance(s) (OUSD, USDT, USDC, DAI, ETH)
        """
        FUTURE: If speed is concern, will need to sort out handling this asynchronously
        """
        ousd_balance = round(eth.get_token_balance(OUSD, user, LATEST_BLOCK) / 1e18, 2)
        usdt_balance = round(eth.get_token_balance(USDT, user, LATEST_BLOCK) / 1e6, 2)
        usdc_balance = round(eth.get_token_balance(USDC, user, LATEST_BLOCK) / 1e6, 2)
        dai_balance = round(eth.get_token_balance(DAI, user, LATEST_BLOCK) / 1e18, 2)
        total = ousd_balance + usdt_balance + usdc_balance + dai_balance

        # Get the current ETH balance for the user
        eth_balance = float(round(eth.wei_to_ether(eth.get_balance(user, LATEST_BLOCK)), 2))

        # Retrieve the number of transactions the user has initiated
        num_transactions = eth.get_transaction_count(user, LATEST_BLOCK)

        # Get the first transaction initiated by the user
        first_tx = user_details[3]

        # Get the number of OUSD Transactions for user
        num_ousd_logs = len(user_interaction[user])

        # Get the earliest block a user has an OUSD Transfer Event for
        first_event_block = min(user_interaction[user])
        first_event_timestamp = eth.get_block_data(first_event_block)["timestamp"]

        # Get the address age at time of first OUSD Transaction (if first_tx != 0)
        address_age_ousd = 0
        if first_tx != 0:
            address_age_ousd = seconds_to_days(first_event_timestamp - first_tx)

        # Get the latest block a user has an OUSD Transfer Event for
        last_event_block = max(user_interaction[user])
        last_event_timestamp = eth.get_block_data(last_event_block)["timestamp"]

        # Get the total OUSD activity period, in days
        ousd_days_active = seconds_to_days(last_event_timestamp - first_event_timestamp)

        # Check if the address is a contract
        is_contract = user_details[2]

        # Add data to output list
        output.append([
            user, user_ens, ousd_balance, usdt_balance, usdc_balance, dai_balance, total, eth_balance, 
            is_contract, num_transactions, num_ousd_logs, address_age_ousd, first_event_block, 
            first_event_timestamp, last_event_block, last_event_timestamp, ousd_days_active, first_tx
        ])

        i+=1

    # Dump OUSD data to CSV
    output_path = "files/output"
    output_name = "ousd_" + str(LATEST_BLOCK) + ".csv"
    data.save(output, output_path, output_name,
        ["address", "ens", "OUSD", "USDT", "USDC", "DAI", "total", "eth", "is_contract",  "transaction_count",
         "number_ousd_events", "age_first_ousd", "first_seen_block", "first_seen_timestamp", "last_seen_block",
         "last_seen_timestamp", "ousd_days_active", "first_activity"]
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
def seconds_to_days(seconds):
    """
    Function to convert seconds to rounded days
    """
    return round(seconds / (60 * 60 * 24), 2)

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
