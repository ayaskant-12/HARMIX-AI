from config import key
import requests   # web library
from mic_to_text1 import mic1

def chat1(chat):
    messages = []    # list to store all the responses
    system_message = "You are an AI bot, your name is Jarvis"
    message = { "role":"user","parts":[{"text":system_message+" "+chat}]}
    messages.append(message)
    data = { "contents" : messages }
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key="+key
    response = requests.post(url, json=data )

    t1 = response.json()
    # print(t1)
    t2 = t1.get("candidates")[0].get("content").get("parts")[0].get("text") 
    print(t2)


chat = mic1()
# chat = input("Enter the Query: ")
# chat = "who is MS Dhoni"     #   {'candidates': [{'content': {'parts': [{'text': 'Greetings. I
chat1(chat)

