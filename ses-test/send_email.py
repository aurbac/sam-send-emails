import boto3
import os
from botocore.exceptions import ClientError
import json

ses = boto3.client('ses')
s3 = boto3.client('s3')

filename = "base.html"
s = open(filename, 'r').read()

email = os.environ['SENDER_EMAIL']
destination = os.environ['DESTINATION_EMAIL']
name = os.environ['DESTINATION_NAME']
reply = "no-reply@kabits.com"
tags = [ { 'Name' : 'Name', 'Value' : name }]

bucket_name = os.environ['BUCKET_NAME']
object_name = 'files/tokyo-skytree.pdf'
expiration = 86400
values = { 'NAME' : name, 'URL_FILE': '', 'TITLE_FILE': 'Tokyo SkyTree' }

subject = 'Download file from URL: '+values['TITLE_FILE']

try:
    response_url = s3.generate_presigned_url('get_object',
        Params={'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn=expiration)
    print(response_url)
    values['URL_FILE'] = response_url
except ClientError as e:
    print("Unexpected error: %s" % e)

s = s.replace('{{NAME}}', values['NAME'])
s = s.replace('{{URL_FILE}}', values['URL_FILE'])
s = s.replace('{{TITLE_FILE}}', values['TITLE_FILE'])

response = ses.send_email(
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
    Message={
        'Subject': {
            'Data': subject,
            'Charset': 'utf-8'
        },
        'Body': {
            'Text': {
                'Data': 'Text plain',
                'Charset': 'utf-8'
            },
            'Html': {
                'Data': s,
                'Charset': 'utf-8'
            }
        }
    },
)

print(response)