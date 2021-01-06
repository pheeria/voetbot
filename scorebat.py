import re
import requests

API = 'https://www.scorebat.com'
YT = 'https://www.youtube.com/watch?v='
COUNTRIES = [
    'SPAIN',
    'GERMANY',
    'ENGLAND'
]

def find_teams_per_country(country):
    games = requests.get(API + '/video-api/v1').json()
    result = set()
    for game in games:
        competition = game['competition']['name']
        if country in competition:
            result.add(game['side1']['name'])
            result.add(game['side2']['name'])
    return games, sorted(result)

def find_games_per_team(games, team):
    return [g for g in games if team in g['title']]

def prepare_api_links(games):
    result = []
    for game in games:
        match = re.search(r"embed\/g\/(\d+)\/", game['embed'])
        if match:
            result.append(API + '/api/feed/game/sc' + match.group(1))
    return result

def prepare_youtube_videos(apis):
    result = []
    for api in apis:
        response = requests.get(api).json()
        videos = response['response']['v']
        for video in videos:
            result.append(YT + video['si'])
    return result

