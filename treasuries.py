#! Python3
"""
    File name: treasuries.py
    Author: Jonathan Snow
    Date created: 10/21/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to determine balances of Protocol treasuries.
        - UGLY as contract list has expanded over time, makes more sense to hack together
        rather than optimizing as this will not be used regularly.

"""

# Imports
import sys
import requests
from modules import data, eth

# Globals
DEBUG = False
ETH_PRICE = float(eth.get_eth_price())
LATEST_BLOCK = eth.get_latest_block()

# Contracts
# X = eth.get_contract("")
USDC = eth.get_contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
AUSDCV1 = eth.get_contract("0x9bA00D6856a4eDF4665BcA2C2309936572473B7E")
AUSDCV2 = eth.get_contract("0xBcca60bB61934080951369a648Fb03DF4F96263C")
USDT = eth.get_contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")
AUSDTV1 = eth.get_contract("0x71fc860F7D3A592A4a98740e39dB31d25db65ae8")
AUSDTV2 = eth.get_contract("0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811")
DAI  = eth.get_contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")
ADAIV1 = eth.get_contract("0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d")
ADAIV2 = eth.get_contract("0x028171bCA77440897B824Ca71D1c56caC55b68A3")
WETH = eth.get_contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
STETH = eth.get_contract("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")

# NOV 28 ADDITIONS
CEL = eth.get_contract("0xaaAEBE6Fe48E54f431b0C390CfaF0b017d09D42d")
FTT = eth.get_contract("0x50D1c9771902476076eCFc8B2A83Ad6b9355a4c9")
USTC = eth.get_contract("0xa47c8bf37f92aBed4A126BDA807A7b7498661acD")
BUSD = eth.get_contract("0x4Fabb145d64652a948d72533023f6E7A623C7C53")
FRAX = eth.get_contract("0x853d955aCEf822Db058eb8505911ED77F175b99e")
USDP = eth.get_contract("0x8E870D67F660D95d5be530380D0eC0bd388289E1")
TUSD = eth.get_contract("0x0000000000085d4780B73119b644AE5ecd22b376")
USDD = eth.get_contract("0x0C10bF8FcB7Bf5412187A595ab97a3609160b5c6")
GUSD = eth.get_contract("0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd")

CUSDC = eth.get_contract("0x39AA39c021dfbaE8faC545936693aC917d5E7563")
CUSDT = eth.get_contract("0xf650C3d88D12dB855b8bf7D11Be6C55A4e07dCC9")
CDAI = eth.get_contract("0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643")

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
            'aave': ["0x25F2226B597E8F9514B3F68F00f494cF4f286491", "0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c"]
        }

    # Process all treasuries within the DAO
    treasury_balances = get_balances(treasuries)

    # Dump data to list
    output_list = []
    for each in treasury_balances:

        """ UPDATE FOR NEW TOKENS """
        output_list.append(
            [
                each["name"],
                each["usdc"],
                each["ausdc"],
                each["usdt"],
                each["ausdt"],
                each["dai"],
                each["adai"],
                each["weth"],
                each["steth"],
                each["eth"],
                each["busd"],
                each["usdp"],
                each["tusd"],
                each["usdd"],
                each["gusd"],
                each["usd_value"],
                each["cel"],
                each["ftt"],
                each["ustc"],
                each["frax"],
                each["cusdc"],
                each["cusdt"],
                each["cdai"]

            ]
        )

    # Dump treasury data to CSV
    output_path = "files/output"
    output_name = "treasury_" + str(LATEST_BLOCK) + ".csv"

    """ UPDATE FOR NEW TOKENS """
    data.save(output_list, output_path, output_name,
        ["Name", "USDC", "aUSDC", "USDT", "aUSDT", "DAI", "aDAI", "WETH", "stETH", "ETH", "BUSD",
        "USDP", "TUSD", "USDD", "GUSD", "USD_VALUE", "CEL", "FTT", "USTC", "FRAX", "cUSDC", "cUSDT", "cDAI"]
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
def get_balances(input):
    """
    Helper script to loop over treasury dict and 
    to retrieve the balances for each DAO.
    """

    output = []

    # Iterate over treasury values
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

    # Set up output variables
    usdc_balance = 0
    ausdc_balance = 0
    usdt_balance = 0
    ausdt_balance = 0
    dai_balance = 0
    adai_balance = 0
    weth_balance = 0
    steth_balance = 0
    eth_balance = 0
    cel_balance = 0
    ftt_balance = 0
    ustc_balance = 0
    busd_balance = 0
    frax_balance = 0
    usdp_balance = 0
    tusd_balance = 0
    usdd_balance = 0
    gusd_balance = 0
    cusdc_balance = 0
    cusdt_balance = 0
    cdai_balance = 0

    # Process balances for known addresses for DAO
    for address in addresses:

        # Ensure that address is the checksum version
        address = eth.get_checksum(address)

        # Get USDC balances
        usdc_balance += round(eth.get_token_balance(USDC, address, LATEST_BLOCK) / 1e6, 2)
        ausdc_balance += round(eth.get_token_balance(AUSDCV1, address, LATEST_BLOCK) / 1e6, 2)
        ausdc_balance += round(eth.get_token_balance(AUSDCV2, address, LATEST_BLOCK) / 1e6, 2)

        # Get USDT balances
        usdt_balance += round(eth.get_token_balance(USDT, address, LATEST_BLOCK) / 1e6, 2)
        ausdt_balance += round(eth.get_token_balance(AUSDTV1, address, LATEST_BLOCK) / 1e6, 2)
        ausdt_balance += round(eth.get_token_balance(AUSDTV2, address, LATEST_BLOCK) / 1e6, 2)

        # Get DAI balances
        dai_balance += round(eth.get_token_balance(DAI, address, LATEST_BLOCK) / 1e18, 2)
        adai_balance += round(eth.get_token_balance(ADAIV1, address, LATEST_BLOCK) / 1e18, 2)
        adai_balance += round(eth.get_token_balance(ADAIV2, address, LATEST_BLOCK) / 1e18, 2)
        
        # Get ETH wrapper balances
        weth_balance += round(eth.get_token_balance(WETH, address, LATEST_BLOCK) / 1e18, 2)
        steth_balance += round(eth.get_token_balance(STETH, address, LATEST_BLOCK) / 1e18, 2)

        # Get ETH balance
        eth_balance += round(eth.get_balance(address, LATEST_BLOCK) / 1e18, 2)

        # Get more random balances
        cel_balance += round(eth.get_token_balance(CEL, address, LATEST_BLOCK) / 1e4, 2)
        ftt_balance += round(eth.get_token_balance(FTT, address, LATEST_BLOCK) / 1e18, 2)
        ustc_balance += round(eth.get_token_balance(USTC, address, LATEST_BLOCK) / 1e18, 2)
        frax_balance += round(eth.get_token_balance(FRAX, address, LATEST_BLOCK) / 1e18, 2)
        busd_balance += round(eth.get_token_balance(BUSD, address, LATEST_BLOCK) / 1e18, 2)
        usdp_balance += round(eth.get_token_balance(USDP, address, LATEST_BLOCK) / 1e18, 2)
        tusd_balance += round(eth.get_token_balance(TUSD, address, LATEST_BLOCK) / 1e18, 2)
        usdd_balance += round(eth.get_token_balance(USDD, address, LATEST_BLOCK) / 1e18, 2)
        gusd_balance += round(eth.get_token_balance(GUSD, address, LATEST_BLOCK) / 1e2, 2)

        cusdc_balance += round(eth.get_token_balance(CUSDC, address, LATEST_BLOCK) / 1e8, 2)
        cusdt_balance += round(eth.get_token_balance(CUSDT, address, LATEST_BLOCK) / 1e8, 2)
        cdai_balance += round(eth.get_token_balance(CDAI, address, LATEST_BLOCK) / 1e8, 2)


    # Determine the USD value of holdings listed above
    usd_value = usdc_balance + ausdc_balance + usdt_balance + ausdt_balance + dai_balance + adai_balance \
                + (weth_balance * ETH_PRICE) + (steth_balance * ETH_PRICE) + (eth_balance * ETH_PRICE) \
                + busd_balance + usdp_balance + tusd_balance + usdd_balance + gusd_balance

    # Test output
    if DEBUG:
        print("USDC: " + str(usdc_balance))
        print("aUSDC: " + str(ausdc_balance))
        print("USDT: " + str(usdt_balance))
        print("aUSDT: " + str(ausdt_balance))
        print("DAI: " + str(dai_balance))
        print("aDAI: " + str(adai_balance))
        print("WETH: " + str(weth_balance))
        print("STETH: " + str(steth_balance))
        print("ETH: " + str(eth_balance))
        print("USD: " + str(usd_value))

    # Build output dict
    output = {
        'usdc': usdc_balance,
        'ausdc': ausdc_balance,
        'usdt': usdt_balance,
        'ausdt': ausdt_balance,
        'dai': dai_balance,
        'adai': adai_balance,
        'weth': weth_balance,
        'steth': steth_balance,
        'eth': eth_balance,
        'busd': busd_balance,
        'usdp': usdp_balance,
        'tusd': tusd_balance,
        'usdd': usdd_balance,
        'gusd': gusd_balance,
        'usd_value': usd_value,
        'cel': cel_balance,
        'ftt': ftt_balance,
        'ustc': ustc_balance,
        'frax': frax_balance,
        'cusdc': cusdc_balance,
        'cusdt': cusdt_balance,
        'cdai': cdai_balance

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
