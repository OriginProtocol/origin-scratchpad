#! Python3
"""
    File name: oeth_balances.py
    Python Version: 3.9.x

"""

from modules import data, eth

LATEST_BLOCK = 18251964 # eth.get_latest_block()

OETH = eth.get_contract("0x856c4Efb76C1D1AE02e20CEB03A2A6a08b0b8dC3")
OUSD = eth.get_contract("0x2A8e1E676Ec238d8A992307B495b45B3fEAa5e86")
OGN = eth.get_contract("0x8207c1FfC5B6804F6024322CcF34F29c3541Ae26")
OGV = eth.get_contract("0x9c354503C38481a7A7a51629142963F98eCC12D0")
VEOGV = eth.get_contract("0x0C4576Ca1c365868E162554AF8e385dc3e7C66D9")

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
    Function to import a list of addresses and process
    the relevant token balances for each address.
    """

    # Import address list
    print("Loading addresses...")
    addresses = data.load("./files/output/oeth_users_" + str(LATEST_BLOCK) + ".csv", False)
    output_list = []
    i = 1
    for address in addresses:
        print("Processing address " + str(i) + "/" + str(len(addresses)) + "...")
        output_list.append(get_balances(address))
        i+=1

    output_path = "files/output"
    output_name = "oeth_balances_" + str(LATEST_BLOCK) + ".csv"
    data.save(output_list, output_path, output_name,
        [
            "address",
            "OETH",
            "OUSD",
            "OGN",
            "OGV",
            "veOGV",
            "USDC",
            "USDT",
            "DAI",
            "ETH",
            "WETH",
            "stETH",
            "wstETH",
            "cbETH",
            "rETH", 
            "frxETH",
            "sfrxETH",
            "sETH2",
            "rETH2"
        ]
    )


##################################################
def get_balances(address):
    """
    Function to determine token balances for a provided
    Ethereum address.
    """

    address = eth.get_checksum(address)

    #oeth_balance_test = get_token_balance(OETH, address, LATEST_BLOCK, 1e18)
    oeth_balance = round(eth.get_token_balance(OETH, address, LATEST_BLOCK) / 1e18, 2)
    ousd_balance = round(eth.get_token_balance(OUSD, address, LATEST_BLOCK) / 1e18, 2)
    ogn_balance = round(eth.get_token_balance(OGN, address, LATEST_BLOCK) / 1e18, 2)
    ogv_balance = round(eth.get_token_balance(OGV, address, LATEST_BLOCK) / 1e18, 2)

    veogv_balance = round(eth.get_token_balance(VEOGV, address, LATEST_BLOCK) / 1e18, 2)

    usdc_balance = round(eth.get_token_balance(USDC, address, LATEST_BLOCK) / 1e6, 2)
    usdt_balance = round(eth.get_token_balance(USDT, address, LATEST_BLOCK) / 1e6, 2)
    dai_balance = round(eth.get_token_balance(DAI, address, LATEST_BLOCK) / 1e18, 2)

    eth_balance = round(eth.get_balance(address, LATEST_BLOCK) / 1e18, 2)
    
    weth_balance = round(eth.get_token_balance(WETH, address, LATEST_BLOCK) / 1e18, 2)
    steth_balance = round(eth.get_token_balance(STETH, address, LATEST_BLOCK) / 1e18, 2)
    wsteth_balance = round(eth.get_token_balance(WSTETH, address, LATEST_BLOCK) / 1e18, 2)
    cbeth_balance = round(eth.get_token_balance(CBETH, address, LATEST_BLOCK) / 1e18, 2)
    reth_balance = round(eth.get_token_balance(RETH, address, LATEST_BLOCK) / 1e18, 2)
    frxeth_balance = round(eth.get_token_balance(FRXETH, address, LATEST_BLOCK) / 1e18, 2)
    sfrxeth_balance = round(eth.get_token_balance(SFRXETH, address, LATEST_BLOCK) / 1e18, 2)
    seth2_balance = round(eth.get_token_balance(SETH2, address, LATEST_BLOCK) / 1e18, 2)
    reth2_balance = round(eth.get_token_balance(RETH2, address, LATEST_BLOCK) / 1e18, 2)

    output = [
        address,
        oeth_balance,
        ousd_balance,
        ogn_balance,
        ogv_balance,
        veogv_balance,
        usdc_balance,
        usdt_balance,
        dai_balance,
        eth_balance,
        weth_balance,
        steth_balance,
        wsteth_balance,
        cbeth_balance,
        reth_balance,
        frxeth_balance,
        sfrxeth_balance,
        seth2_balance,
        reth2_balance
    ]

    return output

##################################################
def get_token_balance(contract, address, block, base):
    """
    Function to return the balance of a token for 
    a given address.
    """
    return round(eth.get_token_balance(contract, address, block) / base, 2)

##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
