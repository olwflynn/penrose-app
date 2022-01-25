
import os, yaml

## Tests for adding new contracts via the UI and asserting that they are added to the yaml file.



#
# def load_yaml():
#     with open(os.path.join(basedir, 'contracts.yml'), 'r') as stream:
#         contracts_yaml = yaml.safe_load(stream)
#         return contracts_yaml
#
# def write_yaml(updated_yaml):
#     with open(os.path.join(basedir, 'test_contracts.yml'),'w') as yamlfile:
#         yaml.safe_dump(updated_yaml, yamlfile)


def test_contract_added_to_yaml_file(client, tmpdir):

    """
    GIVEN the user
    WHEN adding new contract
    THEN check it has been added to the yaml file
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    print(basedir, 'THIS IS THE BASE PATH')

    p = tmpdir.mkdir("sub").join("contracts.yml")
    CONTENT = "contracts:"
    p.write(CONTENT)
    response = client.post('/api/v1/contract',
                data={'contract_address':'0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
                          'contract_abi':'[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address","name": "user", "type": "address"}]}]'})

    print(p)
    with open(p, 'r') as stream:
        contract_added_to_yaml = yaml.safe_load(stream)

        print(contract_added_to_yaml)
        list_of_contracts_in_yaml = 'tests'
        contract_abi = '[{"anonymous": false}]'
        assert '0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d' in list_of_contracts_in_yaml
        assert '[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address","name": "user", "type": "address"}]}]' is contract_abi