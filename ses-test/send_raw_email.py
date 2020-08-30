import boto3
import os
from botocore.exceptions import ClientError
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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

subject = 'Download file from URL and attachment: '+values['TITLE_FILE']

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


# The full path to the file that will be attached to the email.
ATTACHMENT = "tokyo-skytree.pdf"

# The email body for recipients with non-HTML email clients.
BODY_TEXT = "Hello,\r\nPlease see the attached file for a list of customers to contact."

# The HTML body of the email.
BODY_HTML = s

# The character encoding for the email.
CHARSET = "utf-8"

# Create a multipart/mixed parent container.
msg = MIMEMultipart('mixed')
# Add subject, from and to lines.
msg['Subject'] = subject
msg['From'] = email 
msg['To'] = destination

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
        Source=email,
        Destinations=[
            destination
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