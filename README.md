# Stream web3 events

## Goal
Learn about kafka and building an app to interact with interact it.
Learn about web3 / blockchain events and how to parse important info from them.
Learn about how to materialize events from kafka.

## Setup

### In project folder:

Install dependencies (if you have created a virtualenv for this project make sure you are in it)-->
`pip install -r requirements.txt`

 Start app --> `flask run`

### In src/tests/resources folder
Setup kafka and kowl --> `docker-compose up`

Run tests --> TODO: Add tests

### How to use the app:

The app allows you to add contract addresses and abis for the contracts that you want
to subscribe to their events (note in current MVP version only SimpleStorage contract is allowed).

From here you can hit the subscribe button to start receiving events from these 
contracts. In order to test the firing of events you can you can use the instructions below to

### Create event in contract for subscribed contracts and receive in Kafka

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
localhost:8080. There you have it you will now store all events relating that contract at the click of a button!