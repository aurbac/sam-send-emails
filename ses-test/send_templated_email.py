import boto3
import os
from botocore.exceptions import ClientError
import json

ses = boto3.client('ses')
s3 = boto3.client('s3')

email = os.environ['SENDER_EMAIL']
destination = os.environ['DESTINATION_EMAIL']
name = os.environ['DESTINATION_NAME']
configuration_set_name = os.environ['CONFIGURATION_SET_NAME']
reply = "no-reply@kabits.com"
tags = [ { 'Name' : 'Name', 'Value' : name }]

bucket_name = os.environ['BUCKET_NAME']
object_name = 'files/tokyo-skytree.pdf'
expiration = 86400
values = { 'NAME' : name, 'URL_FILE': '', 'TITLE_FILE': 'Tokyo SkyTree' }

try:
    response_url = s3.generate_presigned_url('get_object',
        Params={'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn=expiration)
    print(response_url)
    values['URL_FILE'] = response_url
except ClientError as e:
    print("Unexpected error: %s" % e)


response = ses.send_templated_email(
    Source=email,
    Destination={
        'ToAddresses': [
            destination,
        ]
    },
    ReplyToAddresses=[
        reply,
    ],
    Tags=tags,
    Template='base',
    TemplateData=json.dumps(values),
    ConfigurationSetName=configuration_set_name
)

print(response)
