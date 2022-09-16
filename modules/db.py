#! Python3
"""
    File name: db.py
    Author: Jonathan Snow
    Date created: 09/06/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to handle SQLite database operations
"""

# Import Standard Packages
from time import time
import sqlite3

CON = sqlite3.connect("./files/ousd.db")
CUR = CON.cursor()

##################################################
def get_block(number):
    """
    Function to get block details from the DB
    """
    res = CUR.execute("SELECT * FROM block WHERE number = ?", (number,))
    return res.fetchone()

##################################################
def add_block(number, timestamp, data):
    """
    Function to add block details to the DB
    """
    last_updated = time()
    CUR.execute(
        "INSERT INTO block (number, timestamp, data, last_updated) VALUES (?,?,?,?);", 
        (number, timestamp, data, last_updated,))
    CON.commit()

##################################################
def get_user(address):
    """
    Function to return a User for a provided address
    if they exist in the DB else return None
    """
    res = CUR.execute("SELECT * FROM user WHERE address = ?", (address,))
    return res.fetchone()

##################################################
def add_user(address, ens, is_contract, first_activity=0):
    """
    Function to add a user to the database and set a
    default first_tx value to 0 unless provided
    """
    last_updated = time()
    CUR.execute(
        "INSERT INTO user (address, ens, is_contract, first_activity, last_updated) VALUES (?,?,?,?,?);", 
        (address, ens, is_contract, first_activity, last_updated,)
    )
    CON.commit()

##################################################
def update_user(address, ens, is_contract, first_activity):
    """
    Function to update a user in the database. Maintaining this
    function in the event data needs to be reprocessed.
    """
    last_updated = time()
    CUR.execute(
        "UPDATE user SET ens=?, is_contract=?, first_activity=?, last_updated=? WHERE address=?;",
        (ens, is_contract, first_activity, last_updated, address,)
    )
    CON.commit()
