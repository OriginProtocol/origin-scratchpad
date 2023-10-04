#! Python3

from modules import data, eth
import sys

OETH = eth.get_contract("0x856c4Efb76C1D1AE02e20CEB03A2A6a08b0b8dC3")

##################################################
def main():
    """
    Function to import a list of blocks to check
    the total supply returned from the contract.
    """

    # Import address list
    print("Loading blocks...")
    blocks = data.load("./files/input/block_data.csv", True)
    output_list = []
    block_count = len(blocks)

    for block in blocks:
        block_number = int(block[2])
        row_number = block[0]
        print("Processing block " + str(row_number - block_count + 1) + "/" + str(block_count) + "...")
        block_data = [block[2], eth.get_total_supply(OETH, block_number)]
        output_list.append(block_data)

    output_path = "files/output"
    output_name = "oeth_total_supply.csv"
    data.save(output_list, output_path, output_name, ["block", "total_supply"])


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
