#! Python3
"""
    File name: sqlite_setup.py
    Author: Jonathan Snow
    Date created: 08/27/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to help initialize a fresh SQLite DB
        Event table is not used at this time as fetching events in realtime
        takes ~20s. Will need to create a unique key for each event using
        the blockHash + txHash + logIndex. This should cover any possible
        block reorg.
"""

from termcolor import colored
import sqlite3

CON = sqlite3.connect("../files/ousd.db")
CUR = CON.cursor()

##################################################
def main():
    """
    Function to set up the ousd SQLite DB.
    """

    print("\nStarting SQLite setup.")

    # Check if event table exists else create
    create_event_table()

    # Check if block table exists else create
    create_block_table()

    # Check if user table exists else create
    create_user_table()

    print(colored("SQLite setup complete.", 'green'))

##################################################
def create_event_table():
    """
    Function to create the event table in the db
    UNUSED RIGHT NOW
    """
    create_event = """
        CREATE TABLE IF NOT EXISTS event (
            hash TEXT,
            e_from TEXT,
            e_to TEXT
        );
    """
    CUR.execute(create_event)

##################################################
def create_block_table():
    """
    Function to create the block table in the db
    """
    create_block = """
        CREATE TABLE IF NOT EXISTS block (
            number INTEGER PRIMARY KEY,
            timestamp INTEGER,
            data TEXT,
            last_updated INTEGER
        );
    """
    CUR.execute(create_block)

##################################################
def create_user_table():
    """
    Function to create the user table in the db
    """
    create_user = """
        CREATE TABLE IF NOT EXISTS user (
            address TEXT UNIQUE PRIMARY KEY,
            ens TEXT,
            is_contract INTEGER,
            first_activity INTEGER,
            last_updated INTEGER
        );
    """
    CUR.execute(create_user)


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
