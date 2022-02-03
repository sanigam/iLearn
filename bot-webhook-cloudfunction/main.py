import logging
import requests
def webhook(request):
    req = request.get_json( force=True)
    logging.info(str(req))
    try:
        intent_detected = req["queryResult"]["intent"]["displayName"]
    except AttributeError:
        return 'json error'
    logging.info ("Intent: ", intent_detected)

    if intent_detected == "hello.world": #intent with no parameters
        result = helloWorld(req)
        #print(result)
        return {"fulfillmentText": result}
    elif intent_detected == "weather":   #intent with parameter
        result = weather(req)
        #print(result)
        return {"fulfillmentText": result}
    elif intent_detected == "question": 
        try:  
            result = question (req)
        except:
            result = "Issue in serving question intent"
        return {"fulfillmentText": result}
    else:
        return {"fulfillmentText": "Intent could not be found in webhook."}

        


#Functions to be called for each intent detected above


def question (req):
    querytext = req["queryResult"]['queryText']
    question = querytext.split(':')[1].strip()
    q =  { "question": question} 
    #result = str(q) 
    resp = requests.post("https://bertqa-5aorr5lmzq-wl.a.run.app", json = q)
    #result = resp.json()['answer']
    if resp.status_code == 200 :
        result = resp.json()['answer'] 
    else :
        result = "Error in BERTQA App. " + str(resp)
    return result


def helloWorld(req):
    import re
    sess = str(req.get("session"))
    email = re.findall('[^\/]+$', sess)[0]
    return  "Hello World Intent Detected Using Webhook Python Code." + '\nYour Email/Phone/Id: ' +  email 

#Function get weather info for a city
def weather(req): #get weather info for a city

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    parameters = req.get('queryResult').get('parameters')
    city = parameters.get("geo-city")
    #city = "San Jose"

    apiKey='ea3988595863ce37ca4b3f6cdbff67a2'
    # upadting the URL
    URL = BASE_URL + "q=" + city + "&units=imperial"+ "&appid=" + apiKey
    # HTTP request
    response = requests.get(URL)
    # checking the status code of the request
    if response.status_code == 200:
        # getting data in the json format
        data = response.json()
        #print(data)
        
        # getting temperature , wind speed and description
        temp = round(data['main']['temp'])
        spd = round(data['wind']['speed'])
        desc = data['weather'][0]['description']
        return  "In " + city + ", it is "+ str(temp) + "°F with " + desc + "." + " Current wind speed is "+ str(spd) + " mph."
    else:
    # showing the error message
        #print("Error in the HTTP request")
        return "Could not get weather data using open weather API"