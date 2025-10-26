import requests
import time
import csv

def generate(minartists):
    headers = {'User-Agent': 'music finder',}
    s = requests.Session()
    s.headers.update({'User-Agent': 'music finder'})


    r = s.get(f'''https://musicbrainz.org/ws/2/genre/all?fmt=txt''')

    genres = []

    for genre in r.text.split('\n'):
        artists = s.get(f'''https://musicbrainz.org/ws/2/artist/?query=tag:"{genre}"&fmt=json&limit={minartists+1}''')
        while artists.status_code == 503:
            time.sleep(2)
            artists = s.get(f'''https://musicbrainz.org/ws/2/artist/?query=tag:"{genre}"&fmt=json&limit={minartists+1}''')

        if len(artists.json()['artists']) >= minartists:
            genres.append(genre +'\n')

    with open('genres.csv', 'w', encoding='utf-8') as f:
        f.writelines(genres)


generate(80)