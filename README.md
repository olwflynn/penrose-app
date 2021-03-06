# Stream web3 events

## Goal
Learn about kafka and building an app to interact with interact it.
Learn about web3 / blockchain events and how to parse important info from them.
Learn about how to materialize events from kafka. For now we pushed events to a discord channel

## Setup

### In project folder:

Create a .env file with the following variables defined (.env file is not pushed to git as it will enable you to store secrets in the future):

```DEBUG=True
FLASK_ENV=development
FLASK_APP=src.main.app.py

TOPIC_NAME = "TRANSACTIONS"
KAFKA_SERVER = "localhost:9093"
KOWL_SERVER ="localhost:8080"
LOCAL_INFURA_URL = "http://127.0.0.1:8545"

PUBLIC_INFURA_URL = "https://mainnet.infura.io/v3/{project_id}"

DEV_MNEMONIC="{DEV_MNEMONIC}"

DISCORD_WEBHOOK_URL="{DISCORD_WEBHOOK_URL}"

#local or public blockchain. Set to false if developing locally
PUBLIC_BLOCKCHAIN=True
```

Install dependencies (if you have created a virtualenv for this project make sure you are in it)-->
`pip install -r requirements.txt`

 Start app --> `flask run`

### In src/tests/resources folder
Setup kafka and kowl --> `docker-compose up`

Run tests --> pytest

### How to use the app:

The app allows you to add contract addresses and abis for the contracts that you want
to subscribe to their events (note in current MVP version only SimpleStorage contract is allowed).

From here you can hit the subscribe button to start receiving events from these 
contracts. In order to test the firing of events you can you can use the instructions below to:

### Create event in smart contract for subscribed contracts and receive in Kafka

First, make sure you have followed the above setup instructions for the app, kafka and kowl

Next, we will spin up a development blockchain using truffle,
deploy a contract to it, subscribe to it in the app and send a transaction to the contract.
This contract will emit an event which will be picked up by the app and 
which will then produce to a kafka topic.

Start development blockchain --> (in client directory) `truffle develop`

Compile the SimpleStorage contract --> (in truffle console) `truffle compile`

Migrate the SimpleStorage contract to the development blockchain--> (in truffle console) `truffle migrate`

Get the address of the contract --> (in truffle console) `contractInstance = await SimpleStorage.deployed()`
then `contractInstance.address`

Copy and paste this address into the src/main/contracts.yml file overwriting one of the other addresses

Reload localhost:5000 and press `Subscribe` for the contract address of the contract you just wrote to the blockchain. 
You are now subscribing to all this contract's events!

Now we should create an event by going back to the truffle console and mutating the contract -->
`contractInstance = await SimpleStorage.set('1234')`

As this contract was mutated it will emit an event. We can check this by going to our kafka viewer Kowl at 
localhost:8080. There you have it you will now store all events relating                that contract at the click of a button!


### Running on mainnet for BAYC smart contract

Bored Ape Yacht Club NFTs are trading at multiple $100k and so I thought it would be interesting to leverage this 
platform to subscribe to events from this smart contract and send them to a discord channel to enable quick access to 
events such as when ownership is transferred along with the addresses and tokenID of the parties involved.

By connecting to mainnet by updating the infura_url and setting the public_blockchain=True in the .env file you can subscribe to
the BAYC contract too! The address of the smart contract is already setup in the initial setup so you just need to subscribe to
`Contract address: 0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D`