#! Python3
"""
    File name: eth.py
    Author: Jonathan Snow
    Date created: 08/16/2021
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions that handle Ethereum related operations, including
        network calls, data manipulation, and other Ethereum specific items.

        Notes:
        - Will standardize code comment structure in the future.
        - May move API keys to ENV
"""

from web3 import Web3
from ens import ENS
from modules import config, db, data
from time import sleep, time
from termcolor import colored
import requests

DEBUG = False

# Load keys from json
KEYS = config.load("modules/settings/keys.json", True)

ETHERSCAN_KEY = KEYS.ETHERSCAN
ETHERSCAN = "https://api.etherscan.io/api"

ALCHEMY_KEY = KEYS.ALCHEMY
ALCHEMY = "https://eth-mainnet.alchemyapi.io/v2/" + ALCHEMY_KEY

# Set up Web3 Object
WEB3 =  Web3(Web3.HTTPProvider(ALCHEMY))
ns = ENS.fromWeb3(WEB3)

# Load ERC20 ABI
ABI = config.load("modules/abi/erc20.json")

##################################################
# Function to get block details
def get_block(block_id, is_full):
    return WEB3.eth.get_block(block_identifier=block_id, full_transactions=is_full)

##################################################
# Function to get block details
def get_block_data(number):

    # Check to see if block exists in DB
    block = db.get_block(number)

    # if block does not exist process and return
    if block is None:
        block_data = WEB3.eth.get_block(block_identifier=number, full_transactions=False)
        block_data_json = WEB3.toJSON(block_data)
        block_data_string = data.json_to_string(block_data_json)

        block_timestamp = block_data["timestamp"]
        db.add_block(number, block_timestamp, block_data_string)

        db_block = db.get_block(number)
        db_block_json = data.string_to_json(db_block[2])
        return db_block_json

    # Else, return block details from DB
    else:
        block_json = data.string_to_json(block[2])
        return block_json

##################################################
# Function to get the latest block processed
def get_latest_block():
    return WEB3.eth.get_block('latest').number

##################################################
# Function to get details about a Transaction
def get_transaction(tx):
    return WEB3.eth.get_transaction(tx)

##################################################
# Function to get a Transaction receipt
def get_transaction_receipt(tx):
    return WEB3.eth.getTransactionReceipt(tx)

##################################################
# Function to initialize a Contract object
def get_contract(address, contract_abi=ABI):
    return WEB3.eth.contract(address=address, abi=contract_abi)

##################################################
# Function to convert from ether to wei
def ether_to_wei(ether):
    return WEB3.toWei(ether, 'ether')

##################################################
# Function to convert from gwei to wei
def gwei_to_wei(gwei):
    return WEB3.toWei(gwei, 'gwei')

##################################################
# Function to convert from gwei to wei
def gwei_to_ether(gwei):
    wei = WEB3.toWei(gwei, 'gwei')
    return WEB3.fromWei(wei, 'ether')

##################################################
# Function to convert from wei to ether
def wei_to_ether(wei):
    return WEB3.fromWei(wei, 'ether')

##################################################
# Function to convert from bytes to int
def bytes2int(bytes):
    return int(bytes.hex(), 16)

##################################################
# Function to get token balance for provided contract
def get_token_balance(contract_object, address, block = get_latest_block()):
    return contract_object.functions.balanceOf(address).call(block_identifier=block)

##################################################
# Function to get ETH balance for provided address
def get_balance(address, block = get_latest_block()):
    return WEB3.eth.get_balance(address, block)

##################################################
# Function to get the current ETH price
def get_eth_price():
    url = ETHERSCAN + "?module=stats&action=ethprice&apikey=" + ETHERSCAN_KEY
    response = get_data(url).json()
    return response["result"]["ethusd"]

##################################################
# Function to take an address and return checksum
def get_checksum(address):
    return WEB3.toChecksumAddress(address)

##################################################
# Function to take an address and return checksum
def get_contract_deploy_date(address, return_block=False):
    """
    Function to try to get the contract deployment
    timestamp from Etherscan data.
    """
    # Generate URL and call Etherscan API
    url = ETHERSCAN + "?module=contract&action=getcontractcreation&contractaddresses=" + address + "&apikey=" + ETHERSCAN_KEY
    response = get_data(url).json()

    # Get the transaction receipt for returned tx
    transaction = response["result"][0]["txHash"]
    tx_receipt = get_transaction_receipt(transaction)

    # Pull the block from the transaction receipt and lookup timestamp
    block = tx_receipt["blockNumber"]
    block_data = get_block_data(block)

    if return_block:
        return block
    else:
        return block_data["timestamp"]

##################################################
# Function to determine if an address is a contract
def is_contract(address):
    data = WEB3.eth.get_code(address)

    if len(data) == 0:
        return False
    else:
        return True

##################################################
def is_contract_verified(address):
    """
    Function to check Etherscan to see if the provided
    contract is verified and returns an ABI.
    """
    url = ETHERSCAN + "?module=contract&action=getabi&address=" + address + "&apikey=" + ETHERSCAN_KEY
    data = get_data(url).json()
    status = int(data["status"])
    
    return True if status == 1 else False

##################################################
# Function to take an address and return checksum
def get_transaction_count(address, block = get_latest_block()):
    return WEB3.eth.get_transaction_count(address, block)

##################################################
# Function to get the first user initiated transaction
def get_first_transaction(address):
    """
    Function to try to get the first user directed transaction
    from Etherscan data.
    """
    # Generate URL and call Etherscan API
    url = ETHERSCAN + "?module=account&action=txlist&address=" + address \
        + "&startblock=0&endblock=99999999&page=1&offset=100&sort=asc&apikey=" + ETHERSCAN_KEY
    response = get_data(url).json()

    # Set default timestamp value in case nothing is found
    timestamp = 0

    # Iterate over transaction list returned from Etherscan
    for each in response["result"]:
        # Look for a transaction by user with the nonce of 0
        if each["from"].lower() == address.lower() and each["nonce"] == "0":
            # Store the timestamp if found, cast to int as ts is String
            timestamp = int(each["timeStamp"])
            break

    return timestamp

##################################################
def get_transfer_logs(contract, from_block, to_block, gap=1000000):
    """
    Function to get all transfer logs for a provided contract.
    NOTE: This can run slowly depending on when the contract was
    deployed and the block gap may need to be adjusted depending
    on the activity within the collection. Designed for a specific
    objective and is not efficient for all collections.
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
        transfer_filter = contract.events.Transfer.createFilter(fromBlock=start_block, toBlock=end_block)
        transfer_entries = transfer_filter.get_all_entries()

        # Log
        if DEBUG: print("Fetched: " + str(start_block) + " to " + str(end_block))

        # Add events to the output list
        output.extend(transfer_entries)

        # Break loop if end_block equals the desired to_block
        if end_block == to_block: break

        # Adjust start_block to be the previous end_block
        start_block = end_block

        # Adjust end_block to the to_block if adding the gap takes us over the 
        # desired to_block, otherwise, add the gap to the new start_block
        end_block = to_block if (start_block + gap) > to_block else (start_block + gap)

    e_time = time()
    print(colored("Retrieved Events in " + str(round(e_time-s_time,2)) + "s", 'green'))
    return output



##################################################
def get_data(url):
    """
    Helper function to get data from a provided URL.
    """
    with requests.Session() as s:
        return s.get(url)

##################################################
def get_ens_name(address):
    """
    Function to lookup the ens name for an address.
    NOTE: Will display a FutureWarning, this can be ignored.
    """
    ens_lookup = ns.name(address)

    if ens_lookup is None:
        return ''
    else:
        return ns.name(address)
