import infermedica_api
import logging
import os, time


INF_APP_ID = ''
INF_APP_KEY = ''
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class SymptomApi(object):
    def __init__(self, sex, age):
        infermedica_api.configure({
            'app_id': INF_APP_ID,
            'app_key': INF_APP_KEY,
            'dev_mode': True  # Use only during development on production remove this parameter
        })

        self.inf_api = infermedica_api.get_api()
        self.sex = sex
        self.age = age
        self.symptoms = {}
        self.last_question = None
        self.condition = None
        #self.conditions = self.inf_api.conditions_list()

    def add_symptom(self, symptomsQuery):
        inf_response = self.inf_api.parse(symptomsQuery).to_dict()
        mentions = inf_response.get("mentions")
        symptoms = {}
        for mention in mentions:
            symptoms[mention.get("id")] = [mention.get("name"), mention.get("choice_id")]
        #{'mentions': [{'choice_id': u'present', 'name': u'Headache', 'orth': u'headache', 'common_name': u'Headache', 'type': u'symptom', 'id': u's_21'}]}
        #{u's_21': u'present'}
        #symptoms['s_1542'] = 'present'
        self.symptoms.update(symptoms)
        
    def get_diagnosis(self):
        print("Starting diagnosis/question finding task...")
        while True:
            diagnose_req = infermedica_api.Diagnosis(sex=self.sex, age=self.age)
            diagnose_req.set_extras("ignore_groups", True)
            for symptom in self.symptoms:
                diagnose_req.add_symptom(symptom, self.symptoms[symptom][1])
            diagnose_res = self.inf_api.diagnosis(diagnose_req).to_dict()
            #{'text': u'Is your headache severe?', 'extras': {}, 'type': u'single', 
            #'items': [{u'choices': [{u'id': u'present', u'label': u'Yes'}, {u'id': u'absent', u'label': u'No'}, {u'id': u'unknown', u'label': u"Don't know"}], u'id': u's_1193', u'name': u'Headache, severe'}]}
            question = diagnose_res.get("question")
            #[{u'common_name': u'Tension-type headaches', u'id': u'c_55', u'probability': 0.0499, u'name': u'Tension-type headaches'}]
            self.condition = diagnose_res.get("conditions")
            if question is not None:
                text = question.get("text")
                # if text in seen_questions:
                #    print("ERROR-- REPEATED QUESTION! EXITING!")
                #    return diagnose_res, None
                # else:
                #    seen_questions.append(text)
                if question.get("type") == "single":
                    self.last_question = {}
                    self.last_question['text'] = question['text']
                    item = question["items"][0]
                    self.last_question['id'] = item['id']
                    self.last_question['name'] = item['name']
                else:
                    #TODO 
                    print("ERROR-- question type not single?")
                    self.last_question = None
                    #items = question.get("items")
                    #for item in items:
                    #    question_symptom_id = item.get("id")
                    #    symptoms[question_symptom_id] = 'unknown'
                    #continue
            return diagnose_res

    def get_condition(self):
        if not self.condition:
            return None
        condition = []
        for c in self.condition:
            condition.append((float(c['probability']), c['common_name']))
        return sorted(condition)[::-1]
        
def main():
    sex = 'male'
    age = '35'
    doctor = Doctor(sex, age)
    symptomsQuery = 'I have a headache'
    doctor.add_symptom(symptomsQuery)
    doctor.get_diagnosis()
    doctor.get_last_question()

if __name__ == '__main__':
    main()
'''
# Create diagnosis object with initial patient information.
# Note that time argument is optional here as well as in the add_symptom function
request = infermedica_api.Diagnosis(sex='male', age=35)

request.add_symptom('Headache', 'present')
request.add_symptom('s_98', 'present')
request.add_symptom('s_107', 'absent')

# call diagnosis
request = api.diagnosis(request)

# Access question asked by API
print(request.question)
print(request.question.text)  # actual text of the question
print(request.question.items)  # list of related evidences with possible answers
print(request.question.items[0]['id'])
print(request.question.items[0]['name'])
print(request.question.items[0]['choices'])  # list of possible answers
print(request.question.items[0]['choices'][0]['id'])  # answer id
print(request.question.items[0]['choices'][0]['label'])  # answer label

# Access list of conditions with probabilities
print(request.conditions)
print(request.conditions[0]['id'])
print(request.conditions[0]['name'])
print(request.conditions[0]['probability'])

# Next update the request and get next question:
# Just example, the id and answer shall be taken from the real user answer
request.add_symptom(request.question.items[0]['id'], request.question.items[0]['choices'][1]['id'])

# call diagnosis method again
request = api.diagnosis(request)
'''
