# TODO
# open results page to correct tab
# carry forward selected genres after submit

from flask import Flask, render_template, request
import csv
import musiclib

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    with open('countries.csv', encoding='utf-8') as f:
        data = csv.reader(f)
        countries = list(data)

    with open('genres.csv', encoding='utf-8') as f:
        allGenres = [i.rstrip() for i in f.readlines()]

    if request.method == 'GET':
        return render_template('index.html', countries=countries,
                                 genres=allGenres)

    if request.method == 'POST':
        
        user = request.form['user']
        country = request.form['country']

        if 'genre' in request.form.keys():

            genres = {i:1 for i in request.form.getlist('genre')}
            print(genres)

        else:

            user = request.form['user']

            try:
                artists = musiclib.get_top_100_lastfm(user)
            except:
                return render_template('index.html', countries=countries, 
                                        error='Error: Invalid username', 
                                        user=user, selected=country, 
                                        genres=allGenres)

            try:
                genres = musiclib.rank_genres(artists)
            except Exception as e:
                return render_template('index.html', countries=countries, 
                                        error='Error: failed to get genres', 
                                        user=user, selected=country, 
                                        genres=allGenres)

        try:
            artistsfound = musiclib.rank_artists_by_country(genres, country)
        except Exception as e:
            print(e)
            return render_template('index.html', countries=countries, 
                                    error='Error: failed to rank artists', 
                                    user=user, selected=country,
                                    genres=allGenres)

        urls = []
        count = 0
        for artist in artistsfound.keys():
            if count >= 10:
                break
            url = artistsfound[artist]['url'][:25] + 'embed' + artistsfound[artist]['url'][24:]
            urls.append(url)
            count += 1

        if count == 0:
            return render_template('index.html', countries=countries, 
                                    error='Sorry, no results could be found', 
                                    user=user, selected=country, genres=allGenres)

        return render_template('index.html', found=True, urls=urls, 
                                countries=countries, user=user, selected=country,
                                genres=allGenres)



if __name__ == '__main__':
    app.run()