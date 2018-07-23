import boto3

#aws ses create-template --cli-input-json file://mytemplate.json
#SES Sandbox

source_email = ''
template_name = 'MyTemplate'
def send_email(email, name, html_msg, text_msg):
    client = boto3.client('ses',
                     region_name="us-east-1")

    data = '{{ "name":"{}", "htmlreport": "{}", "textreport": "{}" }}'.format(name, html_msg, text_msg)
    response = client.send_templated_email(
        Source=source_email,
        Destination={
            'ToAddresses': [
                email,
            ],
        },
        Template=template_name,
        TemplateData=data
    )

def main():
    send_email('', 'violet', "Hello World", "Hi")

if __name__ == "__main__":
    main()
