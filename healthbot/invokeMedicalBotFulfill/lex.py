import logging
import os, time, datetime
import json
import boto3, dynamo, ses

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

MEDICAL_INTENT_NAME = 'MedicalIntent'
NUTRITION_INTENT_NAME='NutritionIntent'
username = None

def fulfill(session_attributes, content):
    logger.debug(content)
    return {
        'sessionAttributes': {},
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": content
                }
            }
    }

def process_report(food_report, symptoms_report):
    html_msg = ""
    text_msg = ""
    html_msg += "Symptoms:<br>"
    text_msg += "Symptoms: "
    for k, v in symptoms_report.items():
        html_msg += "{}: {}<br>".format(k, v)
        text_msg += "{}: {}, ".format(k, v)
    if food_report:
        html_msg += "Food for past one week:<br>"
        text_msg += "Food for past one week:"
        report = {}
        for v in food_report:
            weektime = datetime.datetime.fromtimestamp(int(v[1])).strftime('%Y-%m-%d')
            if weektime not in report:
                report[weektime] = []
            report[weektime].append(v[0])
        for k, v in report.items():
            html_msg += "{}: {}<br>".format(k, ','.join(v))
            text_msg += "{}: {}, ".format(k, ','.join(v))
    return html_msg, text_msg

def get_cognito():
    client = boto3.client('cognito-idp')
    user = client.admin_get_user(UserPoolId="us-east-1_Xq4fJ3U0B", Username=username)
    attr = user['UserAttributes']
    for v in attr:
        if v['Name'] == 'email':
            email = v['Value'].replace('+', '')
    return (email)
    
def medical(intent):
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    symptoms = json.loads(session_attributes['symptoms'])
    #generate report
    symptoms_report = {}
    for v in symptoms.values():
        if v[1] != "unknown":
            symptoms_report[v[0]] = v[1]
    logger.debug(symptoms_report)
    content = ""
    if 'make_appointment' in session_attributes:
        id = session_attributes['make_appointment']
        doctors = json.loads(session_attributes['doctors'])
        content += "This is the phone number of that hospital: {}.".format(doctors[id])
        content += " You can call it later."
    else:
        content += "It's better to go to see a doctor!"
    food_report = dynamo.query_food(username)
    html_msg, text_msg = process_report(food_report, symptoms_report)
    logger.debug(html_msg)
    ses.send_email(get_cognito(), username, html_msg, text_msg)
    return fulfill(session_attributes, content)

def nutrition(intent_request):
    logger.debug(intent_request)
    return fulfill({}, 'Wait up! We are building this feature') 

def dispatch(intent_request):
    #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == MEDICAL_INTENT_NAME:
        return medical(intent_request)
    if intent_name == NUTRITION_INTENT_NAME:
        return nutrition(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    global username
    username = event['userId']
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)
