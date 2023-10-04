#! Python3
"""
    File name: oeth_users.py
    Python Version: 3.9.x

"""

from time import time
from modules import data, eth, db
from termcolor import colored

LATEST_BLOCK = 18251964 # eth.get_latest_block()

ERC20 = eth.get_contract("0x856c4Efb76C1D1AE02e20CEB03A2A6a08b0b8dC3")
USDT = eth.get_contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")
USDC = eth.get_contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
DAI  = eth.get_contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")

##################################################
def main():
    """
    Function to do a bunch of stuff. Not optimized.
    Takes 15 minutes to run...
    """
    print("\nStarting OETH analysis.")

    ousd_transfer_logs = eth.get_transfer_logs(ERC20, LATEST_BLOCK)
    transfer_logs = process_logs(ousd_transfer_logs)
    user_interaction = process_user_logs(transfer_logs)

    users = list(user_interaction.keys())
    users.remove("0x0000000000000000000000000000000000000000")

    output = []
    i = 1
    users_count = len(users)
    for user in users:
        print("\rProcessing user " + str(i) + " / " + str(users_count) + "          ", end="", flush=True)

        user = eth.get_checksum(user)
        user_details = process_user(user)
        user_ens = user_details[1]
        erc20_balance = round(eth.get_token_balance(ERC20, user, LATEST_BLOCK) / 1e18, 2)
        usdt_balance = round(eth.get_token_balance(USDT, user, LATEST_BLOCK) / 1e6, 2)
        usdc_balance = round(eth.get_token_balance(USDC, user, LATEST_BLOCK) / 1e6, 2)
        dai_balance = round(eth.get_token_balance(DAI, user, LATEST_BLOCK) / 1e18, 2)

        eth_balance = float(round(eth.wei_to_ether(eth.get_balance(user, LATEST_BLOCK)), 2))
        num_transactions = eth.get_transaction_count(user, LATEST_BLOCK)
        first_tx = user_details[3]
        num_ousd_logs = len(user_interaction[user])
        first_event_block = min(user_interaction[user])
        first_event_timestamp = eth.get_block_data(first_event_block)["timestamp"]

        address_age_ousd = 0
        if first_tx != 0:
            address_age_ousd = seconds_to_days(first_event_timestamp - first_tx)

        last_event_block = max(user_interaction[user])
        last_event_timestamp = eth.get_block_data(last_event_block)["timestamp"]

        ousd_days_active = seconds_to_days(last_event_timestamp - first_event_timestamp)

        is_contract = user_details[2]

        output.append([
            user, user_ens, erc20_balance, usdt_balance, usdc_balance, dai_balance, eth_balance, 
            is_contract, num_transactions, num_ousd_logs, address_age_ousd, first_event_block, 
            first_event_timestamp, last_event_block, last_event_timestamp, ousd_days_active, first_tx
        ])
        i+=1

    output_path = "files/output"
    output_name = "oeth_users_" + str(LATEST_BLOCK) + ".csv"
    data.save(output, output_path, output_name,
        ["address", "ens", "OETH", "USDT", "USDC", "DAI", "eth", "is_contract",  "transaction_count",
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

        if from_address in output.keys():
            output[from_address] += [block]
        else:
            output[from_address] = [block]

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

    if user_details is None:
        ens_name = eth.get_ens_name(address)
        is_contract = eth.is_contract(address)

        if is_contract:
            first_activity = eth.get_contract_deploy_date(address)
        else:
            first_activity = eth.get_first_transaction(address)

        db.add_user(address, ens_name, is_contract, first_activity)
        user_details = db.get_user(address)

    return user_details

##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
