import boto3

queue_url = 'https://sqs.us-east-1.amazonaws.com/109422881420/diningChatbot'

#sqs = boto3.client('sqs',
#   aws_access_key_id=AWS_ACCESS_KEY,
#   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def build_attribute(attrs):
    res = {}
    for k, v in attrs.items():
        res[k] = {}
        res[k]['DataType'] = 'String'
        res[k]['StringValue'] = v
    return res

def parse_attribute(attrs):
    res = {}
    #u'MessageAttributes': {'grade': {u'DataType': 'String', u'StringValue': 'A'}
    for k, v in attrs.items():
        res[k] = v['StringValue']
    return res

def send_message(msg_attrs, msg_body):
    sqs = boto3.client('sqs')
    msg_attrs = build_attribute(msg_attrs)
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes=msg_attrs,
        MessageBody=msg_body
    )

def receive_message():
    sqs = boto3.client('sqs')
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    if 'Messages' not in response:
        return {}
    msg = response['Messages'][0]
    receipt_handle = msg['ReceiptHandle']
    attrs = parse_attribute(msg['MessageAttributes']) 
    # Delete received message from queue
    sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle)

    return attrs

def main():
    attrs = {}
    attrs['name'] = 'violet'
    attrs['grade'] = 'A'
    #send_message(attrs, "Hello World")
    receive_message()
    
if __name__ == "__main__":
    main()


