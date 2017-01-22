import urllib2
import json
from datetime import date

API_BASE="https://preferredtrainer.com/Alexa/socialCalander.php"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.5cb11d74-1840-4b5a-be30-9ee89f25f84b"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetNextSocial":
        return get_next_social()
    elif intent_name == "GetNextSocialWith":
        return get_next_social_with(intent)
    elif intent_name == "WhenNextSocialDay":
        return get_social_on(intent)
    elif intent_name == "addSocial":
        return addSocial(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Social Calander - Thanks"
    speech_output = "Goodbye Jacob."
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Social Calander"
    speech_output = "Welcome to your social calander. " \
                    "You can ask me when your next social is, or " \
                    "ask me for when you party with a specific sorority.."
    reprompt_text = "Please ask me for things regarding your social calander, " \
                    "for example next party with Kappa Alpha Theta."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_next_social():
    session_attributes = {}
    card_title = "Social Calander"
    reprompt_text = ""
    should_end_session = False
    response = urllib2.urlopen(API_BASE + '?type=next')
    social_status = json.load(response) 
    social_date_split =  social_status["date"].split('-')
    social_date = date(day=int(social_date_split[2]), month=int(social_date_split[1]), year=int(social_date_split[0])).strftime('%A %B %d')
    speech_output = "Your next social is with " + social_status["sorority"].lower() + " on " + social_date + " and the theme is " + social_status["theme"]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def addSocialtheme(intent):
    session_attributes = {}
    card_title = "Social Calander"
    speech_output = "I'm not sure what you said. " \
                    "Please try again."
    reprompt_text = "I'm not sure what you said. " \
                    "You must say a day and a sorority."
    should_end_session = False
    if "sorority" in intent["slots"] and "date" in intent["slots"]:
        sorority_name = intent["slots"]["sorority"]["value"]
        sorority_abv = get_sorority_name(sorority_name.lower())
        date = intent["slots"]["date"]["value"]
        theme = intent["slots"]["theme"]["value"]
        response = urllib2.urlopen(API_BASE + '?type=add&secondary=' + sorority_abv + '&date=' + date + '&theme=' + theme)
        social_status = json.load(response) 
        if(social_status["status"] == "success"):
            speech_output = "Your social with " + sorority_name + " was added."
            reprompt_text = ""
        else:
            speech_output = "The social could not be added. Please Try again."
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def addSocial(intent):
    session_attributes = {}
    card_title = "Social Calander"
    speech_output = "I'm not sure what you said. " \
                    "Please try again."
    reprompt_text = "I'm not sure what you said. " \
                    "You must say a day and a sorority."
    should_end_session = False
    if "sorority" in intent["slots"] and "date" in intent["slots"]:
        sorority_name = intent["slots"]["sorority"]["value"]
        sorority_abv = get_sorority_name(sorority_name.lower())
        date = intent["slots"]["date"]["value"]
        response = urllib2.urlopen(API_BASE + '?type=add&secondary=' + sorority_abv + '&date=' + date)
        social_status = json.load(response) 
        if(social_status["status"] == "success"):
            speech_output = "Your social with " + sorority_name + " was added."
            reprompt_text = ""
        else:
            speech_output = "The social could not be added. Please Try again."
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_next_social_with(intent):
    session_attributes = {}
    card_title = "Social Calander"
    speech_output = "I'm not sure which you wanted your social for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which you wanted your social for. " \
                    "Try Sigma Kappa, or Zeta Tau Alpha for example."
    should_end_session = False
    if "sorority" in intent["slots"]:
        sorority_name = intent["slots"]["sorority"]["value"]
        sorority_abv = get_sorority_name(sorority_name.lower())
        response = urllib2.urlopen(API_BASE + '?type=sorority&secondary=' + sorority_abv)
        social_status = json.load(response) 
        if(social_status):
            reprompt_text = ""
            social_date_split =  social_status["date"].split('-')
            social_date = date(day=int(social_date_split[2]), month=int(social_date_split[1]), year=int(social_date_split[0])).strftime('%A %B %d')
            speech_output = "Your next social with " + get_sorority_pron(sorority_name) + " is on " + social_date + " and the theme is " + social_status["theme"]
        else:
            speech_output = "I am not sure when your next social with " + sorority_name + " is."
            reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_social_on(intent):
    session_attributes = {}
    card_title = "Social Calander"
    speech_output = "I'm not sure which you wanted your social for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which you wanted your social for. " \
                    "Try Next Thursday, or January 9th for example."
    should_end_session = False
    if "Day" in intent["slots"] and (intent["slots"]["Day"]["value"]):
        day = intent["slots"]["Day"]["value"]
        social_date_split =  day.split('-')
        try:
            social_date = date(day=int(social_date_split[2]), month=int(social_date_split[1]), year=int(social_date_split[0])).strftime('%A %B %d')
            response = urllib2.urlopen(API_BASE + '?type=date&secondary=' + day)
            social_status = json.load(response) 
            
            if(social_status['status'] == "success"):
                reprompt_text = response
                speech_output = "On " + social_date + " you have a social with " + social_status["sorority"].lower() + " and the theme is " + social_status["theme"]
            else:
                speech_output = "You do not have any socials planned for " + social_date + "."
                reprompt_text = ""
        except ValueError:
            speech_output = "You have said an invalid date."
            reprompt_text = ""
            
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_sorority_name(sorority_name):
    return {
        "alpha chi omega": "AXO",
        "alpha phi": "Phi",
        "alpha xi delta": "AXiD",
        "chi omega": "Chi O",
        "delta gamma": "DG",
        "gamma phi beta": "G Phi",
        "kappa alpha theta": "Theta",
        "kappa delta": "KD",
        "kappa kappa gamma": "KKG",
        "sigma kappa": "Skrappa",
        "zeta tau alpha": "Zeta",
        "A chi o": "AXO",
        "phi": "Phi",
        "A z d": "AXiD",
        "chi o": "Chi O",
        "d g": "DG",
        "g phi": "G Phi",
        "theta": "Theta",
        "k d": "KD",
        "k k g": "KKG",
        "s k": "Skrappa",
        "skrappa": "skrappa",
        "zeta": "Zeta",
    }.get(sorority_name, "unkn")
    
def get_sorority_pron(sorority_name):
    return {
        "alpha chi omega": "Aye Chi O",
        "alpha phi": "Alpha Phi",
        "alpha xi delta": "Aye Zee Dee",
        "chi omega": "Chi O",
        "delta gamma": "Dee Gee",
        "gamma phi beta": "Gee Phi",
        "kappa alpha theta": "Theta",
        "kappa delta": "Kay Dee",
        "kappa kappa gamma": "Kay Kay Gee",
        "sigma kappa": "Skrappa",
        "zeta tau alpha": "Zeta",
        "A chi o": "AXO",
        "phi": "Phi",
        "A z d": "AXiD",
        "chi o": "Chi O",
        "d g": "DG",
        "g phi": "G Phi",
        "theta": "Theta",
        "k d": "KD",
        "k k g": "KKG",
        "s k": "Skrappa",
        "skrappa": "skrappa",
        "zeta": "Zeta",
    }.get(sorority_name, "unkn")


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
