import json

def test_index(client):

    response = client.get('/')
    assert response.status_code == 200


def test_contract(client):

    data = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
                  'contract_abi':'[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address","name": "user", "type": "address"}]}]'}

    response = client.post('/api/v1/contract', data=data)
    assert response.status_code == 200

def test_contract_bad_data(client):
    bad_data_not_json = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
            'contract_abi':'[{"anonymo"]]'}
    response_not_json = client.post('/api/v1/contract', data=bad_data_not_json)
    assert response_not_json.status_code == 400

    bad_data_invalid_address = {'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d___INVALID',
                          'contract_abi':'[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address","name": "user", "type": "address"}]}]'}
    response_invalid_address = client.post('/api/v1/contract', data=bad_data_invalid_address)
    assert response_invalid_address.status_code == 400