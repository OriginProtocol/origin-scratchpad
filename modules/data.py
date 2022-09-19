#! Python3
"""
    File name: data.py
    Author: Jonathan Snow
    Date created: 03/12/2018
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to save and load data and perform minor
        parsing tasks.

        Notes:
        - Will standardize code comment structure in the future.
"""

# Import Standard Packages
from pathlib import Path
from time import sleep
import json
import os

# Import Other Packages
from termcolor import colored
import pandas as pd

#
# Function to save a data set as CSV
def save(data, path, filename, column_headers):
    try:
        # Check if path exists, else create
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / filename

        # Create dataframe and save to CSV
        df = pd.DataFrame(data, columns=column_headers)
        df.to_csv(filename, index=False, encoding='utf-8')
        sleep(0.1)
        print(colored("    Data saved.", 'green'))
    except Exception as e:
        print(colored("    An error occurred when saving data.", 'red'))
        print(e)

#
# Function to save a dataframe as CSV
def save_dataframe(data, filename, column_headers):
    try:
        data.to_csv(filename, encoding='utf-8', index=True, header=column_headers)
        sleep(0.1)
        print(colored("    Data saved.", 'green'))
    except Exception as e:
        print(colored("    An error occurred when saving data.", 'red'))
        print(e)

#
# Function to save a dataframe as JSON
def save_json(data, path, file):
    # Check if path exists, else create
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = output_dir / file

    try:
        with open(str(filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        sleep(0.1)
        print(colored("    Data saved.", 'green'))
    except Exception as e:
        print(colored("    An error occurred when saving data.", 'red'))
        print(e)

#
# Function to load a CSV
def load(filename, full):
    try:
        df = pd.read_csv(filename, encoding='utf-8')
        if full:
            return df.values.tolist()
        else:
            data = df.values.tolist()
            for x in range(len(data)):
                data[x] = data[x][0]
            assert len(df) == len(data)
            return data
    except Exception as e:
        print("An error occurred when importing search data.")
        print(e)

#
# Function to load and import a JSON compatible file
def load_json(pathname):
    return json.loads((open(pathname, "r", encoding="utf-8")).read())

#
# Function to check whether a file exists on a specified path
def check(path):
    return os.path.isfile(path)

#
# Function to convert a string to json
# Has to be double decoded
def string_to_json(data):
    return json.loads(json.loads(data))

#
# Function to convert json to a string
def json_to_string(data):
    return json.dumps(data)

