## Data Scripts

A scratchpad for data related scripts. Code is sometimes broken into supporting modules, however
the rest of the code is a proof of concept in many cases. There is likely code duplication, and
other issues that go against traditional best practices.

## Setup

You will need to make sure to add API keys for Etherscan and Alchemy in './modules/settings/keys.json' 
if you are using a script that leverages './modules/eth.py'. This will likely work with the demo keys,
but you may run into rate limit issues.

```
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r ./requirements.txt
```

## Story Scripts

Scripts take a contract address as command line input and will output some data.

```
# Determine what notable Addresses are holders of a provided collection
python3 notable_holders.py 0xbd3531da5cf5857e7cfaa92426877b022e612cf8

# Determine the top 10 holders of a provided collection
python3 top_holders.py 0xbd3531da5cf5857e7cfaa92426877b022e612cf8

# Determine blue chip overlap for a provided collection
python3 bluechip.py 0xBd3531dA5CF5857e7CfAA92426877b022e612cf8

# Get list of all Addresses that have minted from a provided contract
python3 minters.py 0xBd3531dA5CF5857e7CfAA92426877b022e612cf8
```

## OUSD Scripts

The OUSD data script leverages SQLite to reduce the processing time for future runs. This
will store block data and user data in the DB. The initial run will likely be quite slow
as this has not been optimized at all. Future runs will check the DB for user and/or block
data and will avoid many additional network calls.

```
# Run once when setting up for the first time
cd modules
python3 sqlite_setup.py
cd ..
```

```
# Prepare a CSV data dump of all historical OUSD holders
python3 ousd.py
```