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
import dotenv
import os

import psycopg2
from psycopg2.extras import execute_values

dotenv.load_dotenv()

conn = psycopg2.connect(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASS"), dbname=os.getenv("DB_NAME"), sslmode='require')
cursor = conn.cursor()


##################################################
def get_block(number):
    """
    Function to get block details from the DB.
    """
    cursor.execute(
        f"""
        SELECT * 
        FROM block
        WHERE number = {number}
        """
    )
    return cursor.fetchone()


##################################################
def add_block(number, timestamp, data):
    """
    Function to add block details to the DB.
    """
    last_updated = int(time())
    cursor.execute(
        f"""
        INSERT INTO block (number, timestamp, data, last_updated)
        VALUES ({number}, {timestamp}, {data}, {last_updated})
        """
    )
    conn.commit()


##################################################
def get_user(address):
    """
    Function to return a User for a provided address
    if they exist in the DB else return None.
    """
    cursor.execute(
        f"""
        SELECT * 
        FROM user_address
        WHERE address = '{address}'
        """
    )
    return cursor.fetchone()


##################################################
def add_user(address, ens, is_contract, first_activity=0):
    """
    Function to add a user to the database and set a
    default first_tx value to 0 unless provided.
    """
    last_updated = int(time())
    cursor.execute(
        f"""
        INSERT INTO user_address (address, ens, is_contract, first_activity, last_updated)
        VALUES ('{address}', '{ens}', {is_contract}, {first_activity}, {last_updated})
        """
    )
    conn.commit()


##################################################
def update_user(address, ens, is_contract, first_activity):
    """
    Function to update a user in the database. Maintaining this
    function in the event data needs to be reprocessed.
    """
    last_updated = int(time())
    """
    CUR.execute(
        "UPDATE user SET ens=?, is_contract=?, first_activity=?, last_updated=? WHERE address=?;",
        (ens, is_contract, first_activity, last_updated, address,)
    )
    CON.commit()
    """

def get_unprocessed_user():
    """
    Function to get an unprocessed user from the DB
    """
    cursor.execute(
        f"""
        SELECT base_address
        FROM friend_tech_user
        WHERE status IS NULL
        LIMIT 1
        """
    )
    try:
        return cursor.fetchone()[0]
    except TypeError as e:
        return None

##################################################
def add_friendtech_user(base_address):
    """
    Function to add a user to the database and set a
    default first_tx value to 0 unless provided.
    """
    cursor.execute(
        f"""
        INSERT INTO friend_tech (base_address)
        VALUES ('{base_address}')
        """
    )
    conn.commit()

##################################################
def add_friendtech_metadata(base_address, id, t_un, t_id):
    """
    Function to add a user to the database and set a
    default first_tx value to 0 unless provided.
    """
    cursor.execute(
        f"""
        UPDATE friend_tech_user
        SET
            ft_id = {id},
            twitter_username = '{t_un}',
            twitter_id = {t_id},
            status = 'complete'
        WHERE base_address = '{base_address}'
        """
    )
    conn.commit()

##################################################
def flag_friendtech_user(base_address):
    """
    Function to skip processing for a speciifc base user.
    """
    cursor.execute(
        f"""
        UPDATE friend_tech_user
        SET status = 'skipped'
        WHERE base_address = '{base_address}'
        """
    )
    conn.commit()

