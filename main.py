import requests
from scorebat import prepare_api_links, prepare_youtube_videos, find_games_per_team, find_teams_per_country

API = 'https://www.scorebat.com'
COUNTRIES = [
    'SPAIN',
    'GERMANY',
    'ENGLAND'
]

def main():
    response = requests.get(API + '/video-api/v1').json()
    barcelona = find_games_per_team(response, 'Barcelona')
    print(find_teams_per_country(response, COUNTRIES[2]))

    links = prepare_api_links(barcelona)
    videos = prepare_youtube_videos(links)

    print(videos)

        

if __name__ == '__main__':
    main()
