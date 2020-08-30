import os
import boto3
from botocore.exceptions import ClientError
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def lambda_handler(event, context):
    
    filename = "base.html"
    html = open(filename, 'r').read()

    SENDER_EMAIL = os.environ['SENDER_EMAIL']
    BUCKET_NAME = os.environ['BUCKET_NAME']
    print(json.dumps(event))
    for record in event['Records']:
        email_destination = ''
        name_destination = ''
        s3_key = ''
        if 'EmailDestination' in record['messageAttributes']:
            email_destination = record['messageAttributes']['EmailDestination']['stringValue']
        if 'NameDestination' in record['messageAttributes']:
            name_destination = record['messageAttributes']['NameDestination']['stringValue']
        if 'S3Key' in record['messageAttributes']:
            s3_key = record['messageAttributes']['S3Key']['stringValue']
        if (email_destination!='' and name_destination!='' and s3_key!=''):
            send_email(SENDER_EMAIL, email_destination, name_destination, html, BUCKET_NAME, s3_key)
    return True

def send_email(sender_email, email_destination, name_destination, html, bucket_name, s3_key):
    
    ses = boto3.client('ses')
    s3 = boto3.client('s3')
    
    file_split = s3_key.split('/')
    file_path = '/tmp/'+file_split[len(file_split)-1]
    
    s3.download_file(bucket_name, s3_key, file_path)
    
    reply = "no-reply@kabits.com"
    tags = [ { 'Name' : 'Name', 'Value' : 'Uriel' }]
    
    object_name = s3_key
    expiration = 86400
    values = { 'NAME': name_destination, 'URL_FILE': '', 'TITLE_FILE': 'Tokyo SkyTree' }
    
    subject = 'SQS -> Lambda - Download file from URL and attachment: '+values['TITLE_FILE']
    
    try:
        response_url = s3.generate_presigned_url('get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=expiration)
        print(response_url)
        values['URL_FILE'] = response_url
    except ClientError as e:
        print("Unexpected error: %s" % e)
    
    html = html.replace('{{NAME}}', values['NAME'])
    html = html.replace('{{URL_FILE}}', values['URL_FILE'])
    html = html.replace('{{TITLE_FILE}}', values['TITLE_FILE'])
    
    # The full path to the file that will be attached to the email.
    ATTACHMENT = file_path
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Hello,\r\nPlease see the attached file for a list of customers to contact."
    
    # The HTML body of the email.
    BODY_HTML = html
    
    # The character encoding for the email.
    CHARSET = "utf-8"
    
    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = subject
    msg['From'] = sender_email 
    msg['To'] = email_destination
    
    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')
    
    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    
    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    
    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())
    
    # Add a header to tell the email client to treat this part as an attachment,
    # and to give the attachment a name.
    att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
    
    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)
    
    # Add the attachment to the parent container.
    msg.attach(att)
    #print(msg)
    
    try:
        #Provide the contents of the email.
        response = ses.send_raw_email(
            Source=sender_email,
            Destinations=[
                email_destination
            ],
            RawMessage={
                'Data':msg.as_string(),
            }
        )
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
    return True