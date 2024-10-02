import base64
import json
import os
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime


def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] {word}")

def make_request(method, url, headers, json=None, data=None):
    retry_count = 0
    while True:
        time.sleep(2)
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, json=json)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json, data=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json, data=data)
        else:
            raise ValueError("Invalid method.")
        
        if response.status_code >= 500:
            if retry_count >= 4:
                print_(f"Status Code: {response.status_code} | Server Down")
                return None
            retry_count += 1
        elif response.status_code >= 400:
            print_(f"Status Code: {response.status_code} | Request Failed")
            return None
        elif response.status_code >= 200:
            return response.json()

class Birdx():
    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            # "telegramauth": f"tma {token}",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127", "Microsoft Edge WebView2";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "Referer": "https://birdx.birds.dog/home",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    def get_user_info(self, query):
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        url = "https://birdx-api.birds.dog/user"
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def get_info(self, query):
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        url = 'https://birdx-api2.birds.dog/minigame/incubate/info'
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def upgraded(self, query):
        url = 'https://birdx-api2.birds.dog/minigame/incubate/upgrade'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            if response is not None:
                sec = 3600
                print_(f"Upgraded Success, Level {response.get('level',0)} | Waiting Time : {round(sec*response.get('duration',0))} seconds")
            return response
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def confirm_upgrade(self, query):
        url = 'https://birdx-api2.birds.dog/minigame/incubate/confirm-upgraded'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('post', url, headers)
            return response
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def clear_task(self, query):
        url = "https://birdx-api.birds.dog/project"
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            list_task_complete = self.check_task_completion(query)
            if response is not None:
                for task in response:
                    if task.get('is_enable'):
                        print_(f"Name : {task.get('name','')}")
                        detail_task = task.get('tasks',[])
                        for detail in detail_task:
                            id = detail.get('_id',"")
                            if id in list_task_complete:
                                print_(f"Task {detail.get('title')} : Done")
                            else:
                                print_(f"Starting Task {detail.get('title')}")
                                self.join_task(query, detail)

        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def check_task_completion(self, query):
        url = "https://birdx-api.birds.dog/user-join-task/"
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            list = []
            response = make_request('get', url, headers)
            for data in response:
                task_id = data.get('taskId','')
                list.append(task_id)
            return list
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def join_task(self, query, detail):
        url = 'https://birdx-api.birds.dog/project/join-task'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        payload = {"taskId":detail.get('_id'),
                   "channelId":detail.get('channelId'),
                   "slug":detail.get('slug'),
                   "point":detail.get('point')}
        try:
            list = []
            response = make_request('post', url, headers, json=payload)
            if response is not None:
                print_(f"Task {detail.get('title')} {response.get('msg')}")
            return list
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def join_game(self, query):
        url = 'https://birdx-api2.birds.dog/minigame/egg/join'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            if response is not None:
                turn = response.get('turn')
                while True:
                    if turn <= 0:
                        data_claim_game = self.claim_game(query)
                        if data_claim_game is not None:
                            print_("Total Reward Claimed")
                        break
                    else:
                        data_play = self.play_game(query)
                        if data_play is not None:
                            result = data_play.get('result')
                            data_turn = self.turn_game(query)
                            if data_turn is not None:
                                total = data_turn.get('total')
                                turn = data_turn.get('turn')
                                print_(f"Play game done, Reward : {result} | Total Reward : {total}")


        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def turn_game(self, query):
        url = 'https://birdx-api2.birds.dog/minigame/egg/turn'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            return response

        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def play_game(self, query):
        url = 'https://birdx-api2.birds.dog/minigame/egg/play'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None
    
    def claim_game(self, query):
        url = 'https://birdx-api2.birds.dog/minigame/egg/claim'
        headers = self.headers
        headers['telegramauth'] = f"tma {query}"
        try:
            response = make_request('get', url, headers)
            return response
        except requests.RequestException as e:
            print(f"Failed to fetch user data for token. Error: {e}")
            return None