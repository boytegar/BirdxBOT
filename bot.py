import base64
import json
import os
import random
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime

from birdx import Birdx

def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] {word}")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def load_query():
    try:
        with open('birdx_query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File birdx_query.txt not found.")
        return [  ]
    except Exception as e:
        print("Failed get Query :", str(e))
        return [  ]


def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def remaining_time(times):
    hours, remainder = divmod(times, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"Remaining Time Upgrade : {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds"

def main():
    selector_task = input("auto clear task y/n  : ").strip().lower()
    selector_games = input("auto playing games y/n  : ").strip().lower()
    clear_terminal()
    while True:
        birdx = Birdx()
        queries = load_query()
        sum = len(queries)
        delay = int(1 * random.randint(3600, 3650))
        start_time = time.time()
        for index, query in enumerate(queries, start=1):
            print_(f"========== Account {index}/{sum} ===========")
            print_('Getting Detail User....')
            data_user_info = birdx.get_user_info(query)
            if data_user_info is not None:
                username = data_user_info.get('telegramUserName', 'Unknown')
                telegram_id = data_user_info.get('telegramId', 'Unknown')
                telegram_age = data_user_info.get('telegramAge', 'Unknown')
                total_rewards = data_user_info.get('balance', 0)
                incubationSpent = data_user_info.get('incubationSpent',0)
                print_(f"TGID : {telegram_id} | Name : {username} | Age : {telegram_age} | Reward : {total_rewards}")

                if incubationSpent == 0:
                    birdx.upgraded(query)
                
                data_info = birdx.get_info(query)
                if data_info is not None:
                    level = data_info.get('level',0)
                    status = data_info.get('status',0)
                    print_(f"Level : {level} | Birds : {data_info.get('birds')}")
                    upgradedAt = data_info.get('upgradedAt', 0)/1000
                    duration = data_info.get('duration', 0)
                    now = time.time()
                    upgrade_time = 3600*duration
                    if now >= (upgradedAt+upgrade_time):
                        if status == "confirmed":
                            print_('Upgraded...')
                            birdx.upgraded(query)
                        else:
                            data_confirmed  = birdx.confirm_upgrade(query)
                            if data_confirmed is not None:
                                print_(f"Upgrade Confirmed...")
                                birdx.upgraded(query)
                    else:
                        print_(remaining_time((upgradedAt+upgrade_time) - now))
                
                if selector_task == "y":
                    print_("Start Clear Quest")
                    birdx.clear_task(query)
                
                if selector_games == "y":
                    print_("Start Playing Game")
                    birdx.join_game(query)

            else:
                print_('User Not Found')



        end_time = time.time()
        total = delay - (end_time-start_time)
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        if total > 0:
            print_(f"[ Restarting In {int(hours)} Hours {int(minutes)} Minutes {int(seconds)} Seconds ]")
            time.sleep(total)

if __name__ == "__main__":
     main()