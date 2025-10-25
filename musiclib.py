# TODO: prevent artists with zero releases being included

import requests
import time
from concurrent.futures import ThreadPoolExecutor

# UA to avoid rate limiting
headers = {'User-Agent': 'music finder',}
s = requests.Session()
s.headers.update({'User-Agent': 'music finder'})


with open('LASTFM.txt') as f:
    LASTFM_API_KEY = f.readline()
    if LASTFM_API_KEY == '':
        raise ValueError('No key was found in LASTFM.txt')


# Obtains genres of an artist from their MBID
def get_genres(mbid):
    r = s.get(f'''https://musicbrainz.org/ws/2/artist/{mbid}?fmt=json&inc=genres''')
    while r.status_code == 503:
        time.sleep(1.1)
        r = s.get(f'''https://musicbrainz.org/ws/2/artist/{mbid}?fmt=json&inc=genres''')


    try:
        data = r.json()['genres']
    except:
        return []

    if data == []:
        return []

    maxcount = max([i['count'] for i in data]) # highest 'scored' genre

    genres = []
    
    for i in data:
        # Only genres with 'scores' greater than 1/3 of the maximum are considered
        if i['count'] > (maxcount // 3):
            genres.append(i['name'])
    
    return genres

# OLD GET GENRES TO BE USED WITHOUT MBID
# def get_genres(artist):
#     r = s.get(f'''http://musicbrainz.org/ws/2/artist/?query=name:{artist}&fmt=json&limit=1''', headers=headers)
#     while r.status_code == 503:
#         time.sleep(1.1)
#         r = s.get(f'''http://musicbrainz.org/ws/2/artist/?query=name:{artist}&fmt=json&limit=1''', headers=headers)

#     try:
#         data = r.json()['artists'][0]['tags']
#     except:
#         return []

#     maxcount = max([i['count'] for i in data])

#     genres = []
    
#     for i in data:
#         if i['count'] > (maxcount // 3):
#             genres.append(i['name'])
    
#     return genres


# Scores the relevance of each genre
def rank_genres(artists):
    genres = {}

    # Assigns each genre a score based on how often it appears in the list of artists
    for artist in artists:
        for genre in get_genres(artist):
            if genre in genres.keys():
                genres[genre] += 1 / (len(artists)+1)
            else:
                genres[genre] = 1 / (len(artists)+1)
    
    return {i : genres[i] for i in sorted(genres, key= genres.get, reverse=True)}


# Gets all 100 artists that match a genre and country pair
def get_artists_by_genre_country(genre, country):

    r = s.get(f'''https://musicbrainz.org/ws/2/artist/?query=tag:"{genre}"AND%20country:{country}%20&fmt=json&limit=100''')
    while r.status_code == 503:
        time.sleep(1.1)
        r = s.get(f'''https://musicbrainz.org/ws/2/artist/?query=tag:"{genre}"AND%20country:{country}%20&fmt=json&limit=100''')
    data = r.json()['artists']

    artists = []

    for artist in data:
        genres = {i['name'] : i['count'] for i in artist['tags']}
        maxcount = max(genres.values())

        MINCOUNT = 1 # Lowest maxcount value to be included
        MINFRACTION = 4 # Fraction of maxcount for a genre to be registered

        # Appends all artists who have the given genre with 1/MINFRACTION of their max score and a max score greater than MINCOUNT
        # Last check is to prevent tiny artists being included, but may actually be filtering out too many?
        if genre in genres.keys() and genres[genre] > maxcount // MINFRACTION and maxcount >= MINCOUNT:
            artists.append({'name': artist['name'], 'mbid': artist['id']})

    return artists


def rank_artists_by_country(genres, country):
    artists = {}
    i = 0

    for genre in genres.keys():
        if genres[genre] > min(genres.values()) - 0.01 and i < 10: # excludes lowest scored genres. may not be needed? - 0.01 is a quick fix for when searching by genres, as all genres have same value
            i += 1
            artistsfound = get_artists_by_genre_country(genre, country)
            for artist in artistsfound:
                if artist['name'] in artists.keys():
                    artists[artist['name']]['score'] += genres[genre]
                else:
                    artists[artist['name']] = {'score': genres[genre], 'url': None}
                    artists[artist['name']]['mbid'] = artist['mbid']

    with ThreadPoolExecutor() as exe:
        res = exe.map(get_spotify, [artist['mbid'] for artist in list(artists.values())])

    links = dict(res)

    for artist in list(artists.keys()):
        if artist in links and links[artist] != False:
            artists[artist]['url'] = links[artist]
        else:
            del artists[artist]

    return artists


def get_top_100_lastfm(username):
    r = s.get(f'''http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={username}&api_key={LASTFM_API_KEY}&format=json&limit=30''', headers=headers)
    data = r.json()['topartists']['artist']

    artists = [i['name'] for i in data]
    mbids = [i['mbid'] for i in data]

    return mbids


def get_spotify(mbid):
    
    r = s.get(f'''https://musicbrainz.org/ws/2/artist/{mbid}?fmt=json&inc=url-rels''')
    while r.status_code == 503:
        time.sleep(1.1)
        r = s.get(f'''https://musicbrainz.org/ws/2/artist/{mbid}?fmt=json&inc=url-rels''')

    try:
        data = r.json()['relations']
        name = r.json()['name']
    except:
        return (None, False)

    
    for rel in data:
        if 'spotify.com' in rel['url']['resource']:
            return (name, rel['url']['resource'])

    return (name, False)