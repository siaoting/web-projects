import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

client = boto3.client('lex-runtime')
def handler(event, context):
    responseTemplate = {'type': 'string', 'unstructured': {'id': None, 'text':None, 'lat':None, 'lon':None, 'timestamp':None}}
    result = []
    logger.debug('violet')
    logger.debug(event)
    #logger.debug(context)
    if 'messages' in event:
        for message in event['messages']:
            if 'unstructured' in message:
                unstructuredMessage = message['unstructured']
                if 'text' in unstructuredMessage:
                    name = unstructuredMessage['id']
                    text = unstructuredMessage['text'].lower()
                    lat = unstructuredMessage['lat']
                    lon = unstructuredMessage['lon']
                    response = dict(responseTemplate)
                    lexResponse = client.post_text(
                        botName='MedicalBot',
                        botAlias='pod',
                        userId=name,
                        requestAttributes={'lat':lat, 'lon':lon},
                        inputText=text
                    )
                    logger.debug(lexResponse)
                    response['unstructured']['text'] = lexResponse['message']
                    result.append(response)
                
    return {'messages': result}