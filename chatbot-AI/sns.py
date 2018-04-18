import boto3


def send_message(phone, message):
    client = boto3.client('sns',
            region_name="us-east-1"
    )
   # Publish a message.
    client.publish(PhoneNumber=phone, Message=message)

def main():
    send_message('1917xxxxx', "Hello World")

if __name__ == "__main__":
    main()

