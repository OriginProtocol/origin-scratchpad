#! Python3
"""
    File name: snapshot_members.py
    Author: Jonathan Snow
    Date created: 12/14/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull the followers of a Snapshot Space

"""

# Imports
from time import sleep, time
from modules import data, eth, db, config
from termcolor import colored
import sys
import requests

DEBUG = True

# Globals
URL = "https://hub.snapshot.org/graphql"
LIMIT = 1000

##################################################
def main():
    """
    Function to pull the followers for a provided 
    Snapshot Space ID.
    """
    print("\nFetching Snapshot members.")

    # Build query and make it generic
    space = "cvx.eth"

    # Loop in the event that a space has more than 1,000 members
    follower_data = []
    offset = 0
    while True:
        print("Query # " + str(int((offset/1000) + 1)))
        query = """
            query Followers {
                follows(
                    first: %s,
                    skip: %s,
                    where: {
                    space_in: ["%s"]
                    }
                ) {
                    follower
                    space {
                    id
                    }
                    created
                }
            }
        """%(LIMIT, offset, space)

        # Request data from Snapshot GraphQL endpoint
        response = requests.post(URL, json={'query': query})
        response_data = response.json()["data"]["follows"]

        # Add data to existing list
        follower_data.extend(response_data)

        # Check if there is more data to process
        if len(response_data) != 0:
            offset += LIMIT
        else:
            print("    Processing complete.")
            break


    # Pull follower addresses from GQL data
    followers = []
    for each in follower_data:
        followers.append(each["follower"])

    output = list(set(followers))
    print("Processed " + str(len(output)) + " followers.")

    if DEBUG: sys.exit(0)

    # Dump Follower data to CSV
    output_path = "files/output"
    output_name = "snapshot_followers_" + space + "_" + str(int(time())) + ".csv"
    data.save(output, output_path, output_name, ["address"])

##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
