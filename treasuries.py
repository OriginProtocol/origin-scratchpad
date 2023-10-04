#! Python3
"""
    File name: treasuries.py
    Python Version: 3.9.x
"""

# Imports
import sys
import requests
from modules import data, eth

DEBUG = False
ETH_PRICE = float(eth.get_eth_price())
LATEST_BLOCK = 18251964 # eth.get_latest_block()

USDC = eth.get_contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
USDT = eth.get_contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")
DAI  = eth.get_contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")
WETH = eth.get_contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
STETH = eth.get_contract("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")
WSTETH = eth.get_contract("0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0")
CBETH = eth.get_contract("0xBe9895146f7AF43049ca1c1AE358B0541Ea49704")
RETH = eth.get_contract("0xae78736Cd615f374D3085123A210448E74Fc6393")
FRXETH = eth.get_contract("0x5E8422345238F34275888049021821E8E08CAa1f")
SFRXETH = eth.get_contract("0xac3E018457B222d93114458476f3E3416Abbe38F")
SETH2 = eth.get_contract("0xFe2e637202056d30016725477c5da089Ab0A043A")
RETH2 = eth.get_contract("0x20BC832ca081b91433ff6c17f85701B6e92486c5")


##################################################
def main():
    """
    Function to determine the ownership overlap between the provided
    collection address and bluechip collections.
    """

    # Get list of DAOs to process
    treasuries = get_treasuries()

    if DEBUG:
        treasuries = {
            'aave': [
                "0x25F2226B597E8F9514B3F68F00f494cF4f286491", 
                "0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c"
            ]
        }

    treasury_balances = get_balances(treasuries)

    output_list = []
    for each in treasury_balances:

        """ UPDATE FOR NEW TOKENS """
        output_list.append(
            [
                each["name"],
                each["usdc"],
                each["usdt"],
                each["dai"],
                each["eth"],
                each["weth"],
                each["steth"],
                each["wsteth"],
                each["cbeth"],
                each["reth"],
                each["frxeth"],
                each["sfrxeth"],
                each["seth2"],
                each["reth2"]
            ]
        )

    output_path = "files/output"
    output_name = "treasury_" + str(LATEST_BLOCK) + ".csv"

    """ UPDATE FOR NEW TOKENS """
    data.save(output_list, output_path, output_name,
        ["Name", "USDC", "USDT", "DAI", "ETH", "WETH", "stETH", "wstETH", "cbETH", "rETH", 
         "frxETH", "sfrxETH", "sETH2", "rETH2"]
    )


##################################################
def get_treasuries():
    """
    Function to fetch a list of treasuries from
    the CryptoStats API.
    """
    output = {}
    url = "https://api.cryptostats.community/api/v1/treasuries/currentTreasuryUSD"

    treasuries = get_data(url)["data"]

    for treasury in treasuries:
        tid = treasury["id"]
        output[tid] = treasury["metadata"]["treasuries"]

    return output


##################################################
def get_balances(input):
    """
    Helper script to loop over treasury dict and 
    to retrieve the balances for each DAO.
    """
    output = []
    for key, value in input.items():
        print("Processing: " + str(key))
        balances = get_balance(value)
        balances["name"] = key
        output.append(balances)
    return output


##################################################
def get_balance(addresses):
    """
    Function to determine the token balance for a provided
    Ethereum treasury address.
    UGLY UGLY UGLY
    """

    usdc_balance = 0
    usdt_balance = 0
    dai_balance = 0

    eth_balance = 0
    weth_balance = 0
    steth_balance = 0
    wsteth_balance = 0
    cbeth_balance = 0
    reth_balance = 0
    frxeth_balance = 0
    sfrxeth_balance = 0
    seth2_balance = 0
    reth2_balance = 0

    for address in addresses:

        address = eth.get_checksum(address)

        usdc_balance += round(eth.get_token_balance(USDC, address, LATEST_BLOCK) / 1e6, 2)
        usdt_balance += round(eth.get_token_balance(USDT, address, LATEST_BLOCK) / 1e6, 2)
        dai_balance += round(eth.get_token_balance(DAI, address, LATEST_BLOCK) / 1e18, 2)
        eth_balance += round(eth.get_balance(address, LATEST_BLOCK) / 1e18, 2)
        weth_balance += round(eth.get_token_balance(WETH, address, LATEST_BLOCK) / 1e18, 2)
        steth_balance += round(eth.get_token_balance(STETH, address, LATEST_BLOCK) / 1e18, 2)
        wsteth_balance += round(eth.get_token_balance(WSTETH, address, LATEST_BLOCK) / 1e18, 2)
        cbeth_balance += round(eth.get_token_balance(CBETH, address, LATEST_BLOCK) / 1e18, 2)
        reth_balance += round(eth.get_token_balance(RETH, address, LATEST_BLOCK) / 1e18, 2)
        frxeth_balance += round(eth.get_token_balance(FRXETH, address, LATEST_BLOCK) / 1e18, 2)
        sfrxeth_balance += round(eth.get_token_balance(SFRXETH, address, LATEST_BLOCK) / 1e18, 2)
        seth2_balance += round(eth.get_token_balance(SETH2, address, LATEST_BLOCK) / 1e18, 2)
        reth2_balance += round(eth.get_token_balance(RETH2, address, LATEST_BLOCK) / 1e18, 2)

    output = {
        'usdc': usdc_balance,
        'usdt': usdt_balance,
        'dai': dai_balance,
        'eth': eth_balance,
        'weth': weth_balance,
        'steth': steth_balance,
        'wsteth': wsteth_balance,
        'cbeth': cbeth_balance,
        'reth': reth_balance,
        'frxeth': frxeth_balance,
        'sfrxeth': sfrxeth_balance,
        'seth2': seth2_balance,
        'reth2': reth2_balance

    }

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
