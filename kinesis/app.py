import base64
import json

print('Loading function')

def lambda_handler(event, context):
    output = []

    for record in event['records']:
        print('Payload ID: ' + record['recordId'])
        payload = base64.b64decode(record['data'])

        # Do custom processing on the payload here
        print(payload)

        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(payload).decode('utf-8')
        }
        output.append(output_record)

    print('Successfully processed {} records.'.format(len(event['records'])))

    return {'records': output}
