#! Python3
"""
    File name: config.py
    Author: Jonathan Snow
    Date created: 05/14/2018
    Python Version: 3.9.x
    File Details:
        Purpose: A series of helper functions to convert JSON formatted files
        into usable Python dictionaries.
"""

# Import Standard Packages
from collections import namedtuple
import json
import sys

# Path update
sys.path.append('..')

##################################################
def load(path, to_convert=False):
    """
    Function to load a JSON file from a provided path and 
    return a Python Dictionary
    """
    # Load JSON file from path
    with open(path) as f: file = json.load(f)
    
    # Return object based on input parameter
    if to_convert:
        return convert(file)
    else:
        return file

##################################################
def convert(dictionary):
    """
    Function to convert dictionary into a named tuple
    so that we can access the keys using dot notation.
    """
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)

