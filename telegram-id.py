#!/usr/bin/env python3

import requests
import time

TOKEN = "7343462874:AAFxCdI5-8YKEdW11la4OIWnBt45ogB02hI"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    resp = requests.get(URL + "getUpdates", params=params)
    return resp.json()

def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text}
    requests.post(URL + "sendMessage", params=params)

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "")
                    
                    if text == "/ID":
                        send_message(chat_id, f"L'ID de ce chat est : {chat_id}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()

