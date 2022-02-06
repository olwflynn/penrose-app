import json

def test_index(client):

    response = client.get('/')
    assert response.status_code == 200


def test_contract(client):

    data = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
                  'contract_abi':'[{"anonymous": false,"type":"function" ,"inputs": [{"indexed": false, "internalType": "address","name": "user", "type": "address"}]}]'}

    response = client.post('/api/v1/contract', data=data)
    assert response.status_code == 302

def test_contract_bad_data(client):
    bad_data_not_json = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
            'contract_abi':'[{"anonymo"]]'}
    response_not_json = client.post('/api/v1/contract', data=bad_data_not_json)
    assert response_not_json.status_code == 400

    bad_data_invalid_address = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d___INVALID',
                          'contract_abi':'[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address","name": "user", "type": "address"}]}]'}
    response_invalid_address = client.post('/api/v1/contract', data=bad_data_invalid_address)
    assert response_invalid_address.status_code == 400

    # add case for no type in abi
def test_contract_no_type_in_abi(client):

    bad_data_no_type_in_abi_json = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
            'contract_abi':'[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address","name": "user"}]}]'}
    response_no_type_in_abi_json = client.post('/api/v1/contract', data=bad_data_no_type_in_abi_json)
    assert response_no_type_in_abi_json.status_code == 400

    # add case for no abi and return unknown

def test_contract_no_abi(client):
    no_contract_abi_in_payload = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d'}
    response = client.post('/api/v1/contract', data=no_contract_abi_in_payload)
    assert response.status_code == 302

# add case for subscribing to contract and contract type successful
def test_subscription_to_contract_type_exists(client):

    test_contract_address = '0x270aC7672FfAe74C75400ab00219C770B0Af3409'
    contract_event_type = 'Approval'
    toggle_subscription = 'Subscribe'

    data = {'contract_event_type': contract_event_type, 'toggle_subscription': toggle_subscription}

    response = client.post('/api/v1/contract/{}/subscribe'.format(test_contract_address), data=data)
    print(response)
    assert response.status_code == 302
    # assert

# add case for subscribing to contract and contract changing to active contract
# add case for subscribing to contract and contract subsribing successfully and getting 302
# add case for subscribing to contract and contract subsribing unsuccessfully and getting 400


