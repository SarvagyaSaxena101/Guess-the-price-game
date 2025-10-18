"""
In-memory Game Manager for Guess The Price game.

This is a simple single-process manager suitable for local hosting or small Streamlit apps.
Rooms are stored in a dict keyed by room code. For production you should replace
this with a persistent store (Redis, DB) shared between instances.
"""
import random
import string
import threading
from typing import Dict, Any
from groq_client import fetch_random_item


_lock = threading.Lock()
rooms: Dict[str, Dict[str, Any]] = {}


def _gen_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_room(host_name: str) -> str:
    with _lock:
        code = _gen_code()
        while code in rooms:
            code = _gen_code()
        rooms[code] = {
            'code': code,
            'host': host_name,
            'players': {host_name: {'score': 0}},
            'state': 'lobby',  # lobby | in_round
            'rounds': [],
            'current_round': None,
        }
        return code


def join_room(code: str, player_name: str):
    code = code.upper()
    with _lock:
        if code not in rooms:
            raise ValueError('Room not found')
        room = rooms[code]
        if player_name in room['players']:
            return
        room['players'][player_name] = {'score': 0}


def get_room(code: str):
    return rooms.get(code.upper())


def start_round(code: str):
    code = code.upper()
    with _lock:
        if code not in rooms:
            raise ValueError('Room not found')
        room = rooms[code]
        if room['state'] == 'in_round':
            raise ValueError('Round already in progress')
        # fetch item from GROQ / sanity
        item = fetch_random_item()
        round_no = len(room['rounds']) + 1
        rnd = {
            'round_no': round_no,
            'item': item,
            'guesses': {},  # player -> guess
        }
        room['current_round'] = rnd
        room['state'] = 'in_round'


def submit_guess(code: str, player_name: str, guess: float):
    code = code.upper()
    with _lock:
        if code not in rooms:
            raise ValueError('Room not found')
        room = rooms[code]
        if room['state'] != 'in_round':
            raise ValueError('No round in progress')
        rnd = room['current_round']
        if player_name not in room['players']:
            raise ValueError('Player not in room')
        if player_name in rnd['guesses']:
            raise ValueError('Player already guessed')
        rnd['guesses'][player_name] = float(guess)


def set_round_price(code: str, price: float):
    code = code.upper()
    with _lock:
        if code not in rooms:
            raise ValueError('Room not found')
        room = rooms[code]
        if room['state'] != 'in_round' or not room['current_round']:
            raise ValueError('No round in progress')
        room['current_round']['item']['price'] = float(price)


def end_round(code: str):
    code = code.upper()
    with _lock:
        if code not in rooms:
            raise ValueError('Room not found')
        room = rooms[code]
        if room['state'] != 'in_round':
            raise ValueError('No round in progress')
        rnd = room['current_round']
        true_price = rnd['item'].get('price')
        if true_price is None:
            raise ValueError('Round price is not set. Host must set the correct price before ending the round.')
        # compute diffs
        diffs = []
        for p, g in rnd['guesses'].items():
            diffs.append({'name': p, 'guess': g, 'diff': abs(g - true_price)})
        diffs.sort(key=lambda x: x['diff'])

        winners = []
        # award points: 10,5,1
        points = [10, 5, 1]
        for i, entry in enumerate(diffs[:3]):
            pts = points[i]
            room['players'][entry['name']]['score'] += pts
            winners.append({'name': entry['name'], 'guess': entry['guess'], 'diff': entry['diff'], 'pts': pts})

        rnd['winners'] = winners
        room['rounds'].append(rnd)
        room['current_round'] = None
        room['state'] = 'lobby'


# convenience exports
class Manager:
    def create_room(self, host_name):
        return create_room(host_name)

    def join_room(self, code, player_name):
        return join_room(code, player_name)

    def get_room(self, code):
        return get_room(code)

    def start_round(self, code):
        return start_round(code)

    def submit_guess(self, code, player_name, guess):
        return submit_guess(code, player_name, guess)

    def end_round(self, code):
        return end_round(code)


manager = Manager()
