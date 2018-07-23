import infermedica_api
import logging
import os, time
import symptom, doctor
import json
import boto3
import ast

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

BUCKET_NAME = 'medicalbot'
FILE_NAME = 'medicalDescription.txt'
MEDICAL_INTENT_NAME = 'MedicalIntent'
MAX_SYMPTOMS = 20
username = None

#https://docs.aws.amazon.com/lex/latest/dg/lambda-input-response-format.html
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': {
                "contentType": 'PlainText',
                "content": message
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

def get_status(status):
    if status.find("yes") >= 0:
        return "present"
    elif status.find("no") >= 0:
        return "absent"
    else:
        return "unknown"

def query_appointment(intent, doctor_id):
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    session_attributes['make_appointment'] = doctor_id
    #doctors = json.loads(session_attributes['doctors'])
    #phone = doctors[doctor_id]
    #logger.debug(phone)
    
def query_doctor(intent, slots):
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    intent_name = intent['currentIntent']['name']
    
    if 'conditions' not in session_attributes:
        return 
    conditions = list(ast.literal_eval(session_attributes['conditions']))
    logger.debug(conditions)
    max_percentage, symptom = 0.0, None
    if conditions:
        symptom = conditions[0][1]
        max_percentage = conditions[0][0]
    if not symptom:
        content = "There is no suggestions for doctors"
        slots['appointment'] = 'No'
    else:
        content = "Your maximum possible illnesses is "
        content += symptom + '. '
        symptom = symptom.replace(' ', '+')
        
        lat = intent['requestAttributes']['lat']
        lon = intent['requestAttributes']['lon']
        logger.debug("lat:" + lat + ", lon:" + lon)
        res = doctor.get_doctor(symptom, lat, lon)
        content += "There are {} suggestions for doctors\n".format(len(res))
        doctors = {}
        for i in range(len(res)):
            content += "({}). {}: {}.\n".format(i + 1, res[i][0], res[i][2])
            doctors[i + 1] = res[i][1]
        content += "\nWhich option do you want?"
        if doctors:
            session_attributes['doctors'] = json.dumps(doctors)
    logger.debug(content)
    return elicit_slot(
        session_attributes,
        intent_name,
        slots,
        'doctor',
        content,
    )
    
def query_symptom(intent, slots, symptom_slot, mysymptom):
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    intent_name = intent['currentIntent']['name']
    input = intent['inputTranscript']
    logger.debug('violet')
    logger.debug(session_attributes)
    #Find out symptoms
    if 'pre_question' not in session_attributes:
        symptomsQuery = input
        mysymptom.add_symptom(symptomsQuery)
    else:
        status = input.lower()
        symptom = json.loads(session_attributes['pre_question'])
        mysymptom.symptoms[symptom['id']] = [symptom['name'], get_status(status)]
    if 'symptoms' in session_attributes:
        old = json.loads(session_attributes['symptoms'])
        mysymptom.symptoms.update(old)
    if mysymptom.symptoms:
        session_attributes['symptoms'] = json.dumps(mysymptom.symptoms)
    
    logger.debug(mysymptom.symptoms)
    #diagnosis
    mysymptom.get_diagnosis()
    #Find out next question
    question = mysymptom.last_question
    if not question:
        return elicit_slot(
            session_attributes,
            intent_name,
            slots,
            'symptom',
            "Sorry about that. Can you provide more symptoms?"
        )
    else:
        session_attributes['pre_question'] = json.dumps(question)

    #Find out the conditions
    conditions = mysymptom.get_condition()
    medical_description = get_s3_medical_description()
    if conditions:
        session_attributes['conditions'] = '[' + ', '.join(map(str, conditions)) + ']'
        content = "\n===============================================================\n"
        content += "Possible Illnesses: \n"
        for v in conditions:
            percentage = v[0] * 100.0
            illness = v[1]
            if illness in medical_description:
                medical_url = medical_description[illness]
                content += '<a href="{}" target="_blank">{}</a>: {}%\n'.format(medical_url, illness, percentage)
            else:
                content += '{}: {}%\n'.format(illness, percentage)
        content += "===============================================================\n"
        content += question['text']
    else:
        content = question['text']
    content += "(Please reply with Yes/No/Don't know/Stop asking)"
    return elicit_slot(
        session_attributes,
        intent_name,
        slots,
        'symptom',
        content,
    )

def get_s3_medical_description():
    client = boto3.client('s3', region_name="us-east-1",)
    obj = client.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
    body = obj['Body'].read().decode("utf-8")
    items = body.split('\n')
    medical_description = {}
    for item in items:
        if item:
            des = item.split('#')
            medical_description[des[0]] = des[1]
    return medical_description
    
def get_cognito():
    client = boto3.client('cognito-idp')
    user = client.admin_get_user(UserPoolId="us-east-1_Xq4fJ3U0B", Username=username)
    attr = user['UserAttributes']
    for v in attr:
        if v['Name'] == 'gender':
            sex = v['Value']
        elif v['Name'] == 'birthdate':
            age = str(2018 - int(v['Value'].split('/')[2]))
    return (sex, age)
    
def medical(intent):
    sex, age = get_cognito()
    mysymptom = symptom.SymptomApi(sex, age)
    
    session_attributes = intent['sessionAttributes'] if intent['sessionAttributes'] is not None else {}
    slots = intent["currentIntent"]["slots"]
    symptom_slot = slots["symptom"]
    doctor_slot = slots["doctor"]
    appointment_slots = slots['appointment']
    if appointment_slots:
        if appointment_slots == "yes":
            query_appointment(intent, doctor_slot) 
        return delegate(session_attributes, slots) 
    elif doctor_slot:
        return delegate(session_attributes, slots)
    if symptom_slot and "stop" in symptom_slot.lower():
        return query_doctor(intent, slots)
    else:
        return query_symptom(intent, slots, symptom_slot, mysymptom)

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    logger.debug(intent_name)
    # Dispatch to your bot's intent handlers
    if intent_name == MEDICAL_INTENT_NAME:
        return medical(intent_request)
    # NUTRITION_INTENT_NAME

    raise Exception('Intent with name ' + intent_name + ' not supported')

def handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    global username
    username = event['userId']
    
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)

