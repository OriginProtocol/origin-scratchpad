#! Python3

from modules import db2
from time import sleep
import requests
import sys

SESSION = requests.Session()
API = "https://prod-api.kosetto.com/users/"

##################################################
def main():
    """
    Function to look for unprocessed users and then process.
    """
    address = db2.get_unprocessed_user()

    if address is None:
        print("No addresses to process. Sleeping for 60s...")
        sleep(60)
        return

    print("Processing: " + address)

    metadata = get_metadata(address)

    if metadata.get("message") is not None:
        db2.flag_friendtech_user(address)
    else:
        db2.add_friendtech_metadata(address, metadata["id"], metadata["twitterUsername"], metadata["twitterUserId"])

def get_metadata(address):
    """
    Function to fetch metadata from friend.tech API.
    """
    response = SESSION.get(API + address)
    if response.status_code in [200, 404]:
        return response.json()
    else:
        print("Request Error: " + str(response.status_code))
        sys.exit(0)

##################################################
# Runtime Entry Point
if __name__ == "__main__":

    while True:
        main()
