import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

client = boto3.client('lex-runtime')

def lambda_handler(event, context):

    responseTemplate = {'type': 'string', 'unstructured': {'id': None, 'text':None, 'timestamp':None}}
    result = []
    if 'messages' in event:
        for message in event['messages']:
            if 'unstructured' in message:
                unstructuredMessage = message['unstructured']
                
                if 'text' in unstructuredMessage:
                    inputText = message['unstructured']['text'].lower()
                    response = dict(responseTemplate)
                    
                    lexResponse = client.post_text(
                    botName='DiningConcierge',
                    botAlias='$LATEST',
                    userId= event['name'] if 'name' in event and event['name'] != '' else '',
                    inputText= message['unstructured']['text']
                    )
                    
                    logger.debug(lexResponse)
                    response['unstructured']['text'] = lexResponse['message']
                    result.append(response)
                
    return {'messages': result}
