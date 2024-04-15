#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 13:09:56 2024

@author: simonlesflex
"""
import requests
apiToken = ''
chatID = ''
apiURL = f'https://api.telegram.org/bot{apiToken}/'

def send_to_telegram(message):
    method = "sendMessage"
    try:
        response = requests.post(apiURL + method, json={'chat_id': chatID, 'text': message})
        #response = requests.post(apiURL, json={'text': message})
        print(response.text)
    except Exception as e:
        print(e)
        
def send_photo(chat_id, file_opened):
    method = "sendPhoto"
    params = {'chat_id': chat_id}
    files = {'photo': file_opened}
    resp = requests.post(apiURL + method, params, files=files)
    return resp
        

def send_file(chat_id, file_opened):
    method = "sendDocument"
    params = {'chat_id': chat_id}
    files = {'document': file_opened}
    resp = requests.post(apiURL + method, params, files=files)
    return resp
