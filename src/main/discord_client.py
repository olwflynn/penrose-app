import requests, json

def send_message_to_discord(url, message, parse):
    if parse:
        print(type(message), '- type of message')
        message_json = json.loads(message)
        parsed_message = parse_message(message_json)
    else:
        parsed_message = message
    response = requests.post(url, json={'content': parsed_message})
    return response.status_code


def parse_message(message):
    parsed_message = ''
    args_parsed_keys = ['owner', 'to', 'tokenId']
    other_parsed_keys = ['address', 'blockNumber','event','transactionHash']

    for arg_key in args_parsed_keys:
        try:
            parsed_message = parsed_message + arg_key + ': ' + str(message['args'][arg_key]) + '\n'
        except KeyError:
            print(arg_key, 'is not present')

    for other_key in other_parsed_keys:
        if other_key == 'transactionHash':
            parsed_message = parsed_message + str('https://etherscan.io/tx/{}'.format(message[other_key])) + '\n'
        else:
            try:
                parsed_message = parsed_message + other_key + ': ' + str(message[other_key]) + '\n'
            except KeyError:
                print(other_key, 'is not present')
    return parsed_message

# import json
# data = '''{"args": {"owner": "0xc2A59D94b69f7739F77892677EC875f3629A3F94", "approved": "0x0000000000000000000000000000000000000000", "tokenId": 3311}, "event": "Approval", "logIndex": 330, "transactionIndex": 147, "transactionHash": "0xb65c36c589d1395e89379f7876e09a6727d17bec45eb55f99f86f6e5193747b3", "address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D", "blockHash": "0x34bd50b8750da2a73c9642c9c1d6a0c21752a3f3ec207695bf312de1d5fa252e", "blockNumber": 14375183}
# '''
# message_json = json.loads(data)
#
# print(parse_message(message_json))