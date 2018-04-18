import json
import datetime
import time
import os
import logging
import re

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DINING_SUGGESTION_INTENT_NAME = 'DiningSuggestionsIntent'
GREETING_INTENT_NAME = 'GreetingIntent'
THANKS_INTENT_NAME = 'ThankYouIntent'

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def elicit_intent():
    return {
        "dialogAction": {
            "type": "ElicitIntent",
            "message": {
                "contentType": "PlainText",
                "content": "Hi, How can I help you?"
                }
            }
    }

def fulfill():
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "I am happy that I could assit you with this. :)"
                }
            }
    }
    
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_dining(cuisine, dining_date, dining_time, phone):
    #if appointment_type and not get_duration(appointment_type):
    #    return build_validation_result(False, 'AppointmentType', 'I did not recognize that, can I book you a root canal, cleaning, or whitening?')
    res, err_slot, err_msg = True, None, None
    cuisine_options = ["chinese", "american", "mexican", "taiwanese", "indian", "italian"]
    if cuisine and cuisine.lower() not in cuisine_options:
        res, err_slot = False, 'Cuisine'
        err_msg = 'Sorry, We currently do not support {} as a valid cuisine. Can you try a different one?'.format(cuisine)
    elif dining_date and (dining_date < datetime.datetime.now().strftime('%Y-%m-%d')):
        res, err_slot = False, 'Date'
        err_msg = 'Sorry, I do not suggest the past date. Can you try a different date?'
    elif dining_time and ((dining_date + "-" + dining_time) < datetime.datetime.now().strftime('%Y-%m-%d-%H:%M')):
        res, err_slot = False, 'Time'
        err_msg = 'Sorry, I do not suggest the past time. Can you try a different time?'
    elif phone and (not re.match(r'^\d{10}$', phone)): 
        res, err_slot = False, 'Phone'
        err_msg = 'Sorry, please provide actual phone number.'
        
    return build_validation_result(res, err_slot, err_msg)

def dining(intent):
    slots = intent["currentIntent"]["slots"]
    location = slots["Location"]
    cuisine = slots["Cuisine"]
    dining_date = slots["Date"]
    dining_time = slots["Time"]
    people = slots["PeopleNum"]
    phone = slots["Phone"]
    output_session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    #logger.debug(location, cuisine, dining_time)

    validation_result = validate_dining(cuisine, dining_date, dining_time, phone)
    if not validation_result['isValid']:
        slots[validation_result['violatedSlot']] = None
        return elicit_slot(
            output_session_attributes,
            intent['currentIntent']['name'],
            slots,
            validation_result['violatedSlot'],
            validation_result['message'],
            ""
        )

    return delegate(output_session_attributes, slots)

def dispatch(intent_request):
    #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == DINING_SUGGESTION_INTENT_NAME:
        return dining(intent_request)
    elif intent_name == GREETING_INTENT_NAME:
        return elicit_intent()
    elif intent_name == THANKS_INTENT_NAME:
        return fulfill()

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)

def main():
    context = None
    event = {}
    event["bot"] = {}
    event["bot"]["alias"] = "$LATEST"
    event["bot"]["version"] = "$LATEST"
    event["bot"]["name"] = "DINING"
    event["currentIntent"] = {}
    event["currentIntent"]["name"] = DINING_SUGGESTION_INTENT_NAME
    event["currentIntent"]["slots"] = {}
    event["currentIntent"]["slots"]["Location"] = "New York"
    event["currentIntent"]["slots"]["Cuisine"] = "Chinese"
    event["currentIntent"]["slots"]["Date"] = "2018-03-24"
    event["currentIntent"]["slots"]["Time"] = "21-00"
    event["currentIntent"]["slots"]["PeopleNum"] = "2"
    event["currentIntent"]["slots"]["Phone"] = "1234567890"
    event["sessionAttributes"] = {}
    lambda_handler(event, context)

if __name__ == "__main__":
    main()





