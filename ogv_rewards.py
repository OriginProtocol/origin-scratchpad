#! Python3
"""
    File name: ogv_balances.py
    Python Version: 3.11.x
"""

from modules import data, eth
import requests
import os

BLOCK = 19585500
VEOGV = eth.get_contract("0x0C4576Ca1c365868E162554AF8e385dc3e7C66D9", eth.get_contract_abi("0xE61110663334794abA03c349c621A075DC590a42"))

KEY = os.getenv("DUNE_API_KEY")
QUERY = 3094165
URL = "https://api.dune.com/api/v1/query/" + str(QUERY) + "/results"

SESSION = requests.Session()

##################################################
def main():
    """
    Function to pull some basic data on OGV users.
    """
    output = []

    print("\nStarting OGV reward analysis.")

    # Grab addresses to process

    response = SESSION.get(URL, headers={"x-dune-api-key": KEY}).json()
    results = response["result"]["rows"]

    users_count = len(results)

    output = []
    i = 1
    for row in results:
        address = row["address_raw"]
        user = eth.get_checksum(address)
        print("\rProcessing " + user + ": " + str(i) + " / " + str(users_count) + "          ", end="", flush=True)
        reward = VEOGV.functions.previewRewards(user).call(block_identifier=BLOCK) / 1e18
        output.append([user, reward])
        i+=1

    output_path = "files/output"
    output_name = "ogv_rewards_" + str(BLOCK) + ".csv"
    data.save(output, output_path, output_name, ["address", "reward"])


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
