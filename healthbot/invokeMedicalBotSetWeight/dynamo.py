import boto3
import time, datetime
from boto3.dynamodb.conditions import Key, Attr


TABLE_NAME_WEIGHT = 'medicalbot-weight'
def get_dynamodb():
    client = boto3.resource('dynamodb',
            region_name="us-east-1",
            )
    return client

def put_item_weight(name, weight):
    client = get_dynamodb()
    table = client.Table(TABLE_NAME_WEIGHT)
    response = table.put_item(
        Item={
            'id': name,
            'weight': weight,
            'timestamp': str(int(time.time()))
        })

def get_item_weight(name):
    client = get_dynamodb()
    table = client.Table(TABLE_NAME_WEIGHT)
    response = table.get_item(
        Key={
            'id': name}
        )
    item = response['Item']
    timestamp = item['timestamp']
    weight = item['weight']
    return (timestamp, weight)

def query_weight(name):
    today = time.mktime(datetime.date.today().timetuple())
    tomorrow = today + 86400
    client = get_dynamodb()
    table = client.Table(TABLE_NAME_WEIGHT)
    response = table.query(
        KeyConditionExpression=Key('id').eq(name),
        FilterExpression=Attr('timestamp').between(str(today), str(tomorrow))
    )
    if response['Count'] == 0:
        return None
    print(response['Items'][0]['weight'])
    return response['Items'][0]['weight']

def main():
    name = 'violet'
    #put_item_weight('violet', '54')
    #get_item_weight('violet')
    #query_weight(name)
    #put_item_food('violet', 'egg', '74')
    #get_item_food('violet', '1525485833')
    query_food(name)

if __name__ == '__main__':
    main()
