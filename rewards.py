#! Python3
"""
    File name: paladin.py
    Python Version: 3.11.x

"""
from modules import data
import datetime
import requests
import time

ADDRESS = "0x5De069482Ac1DB318082477B7B87D59dfB313f91"
NOW = int(time.time())

##################################################
def main():
    validator_string = ""
    validators = []
    rewards = 0
    days = 0

    all_validator_data = requests.get(f'https://beaconcha.in/api/v1/validator/eth1/{ADDRESS}').json()
    for each in all_validator_data["data"]:
        validator_string += str(each["validatorindex"]) + ","
        validators.append(each["validatorindex"])

    rewards_data = requests.get(f'https://beaconcha.in/api/v1/validator/{validator_string[:-1]}/performance').json()
    for reward in rewards_data["data"]:
        rewards += reward["performancetotal"]
    
    for validator in validators:
        validator_data = requests.get(f'https://beaconcha.in/api/v1/validator/{validator}').json()
        epoch = validator_data["data"]["activationepoch"]
        epoch_data = requests.get(f'https://beaconcha.in/api/v1/epoch/{epoch}').json()
        timestamp = convert_timestamp(epoch_data["data"]["ts"])
        days_active = (NOW - timestamp) / 86400
        days += days_active
    
        time.sleep(1)

    print("Total Validators: " + str(len(validators)))
    print("Total Rewards: " + str(rewards/1e9))
    print("Total Active Days: " + str(days))


##################################################
def convert_timestamp(timestamp):
    timestamp_format = '%Y-%m-%dT%H:%M:%SZ'
    timestamp_datetime = datetime.datetime.strptime(timestamp, timestamp_format).replace(tzinfo=datetime.timezone.utc)
    return int(timestamp_datetime.timestamp())


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
