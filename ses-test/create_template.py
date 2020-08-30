import boto3
from botocore.exceptions import ClientError

template_name = 'base'
filename = "base.html"
s = open(filename, 'r').read()

ses = boto3.client('ses')

try:
    response = ses.delete_template(TemplateName=template_name)
except ClientError as e:
    print("Unexpected error: %s" % e)

response = ses.create_template(
    Template={
        'TemplateName': template_name,
        'SubjectPart': 'Base template: Download file from URL',
        'TextPart': 'Example of message',
        'HtmlPart': s
    }
)

print(response)