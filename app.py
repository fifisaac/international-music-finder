from flask import Flask, render_template, request
import csv
import musiclib

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    with open('countries.csv', encoding='utf-8') as f:
        data = csv.reader(f)
        countries = list(data)

    if request.method == 'GET':
        return render_template('index.html', countries=countries)

    if request.method == 'POST':
        
        user = request.form['user']
        country = request.form['country']

        try:
            artists = musiclib.get_top_100_lastfm(user)
        except:
            return render_template('index.html', countries=countries, 
                                    error='Error: Invalid username', 
                                    user=user, selected=country)

        try:
            genres = musiclib.rank_genres(artists)
        except Exception as e:
            return render_template('index.html', countries=countries, 
                                    error='Error: failed to get genres', 
                                    user=user, selected=country)

        try:
            artistsfound = musiclib.rank_artists_by_country(genres, country)
        except Exception as e:
            return render_template('index.html', countries=countries, 
                                    error='Error: failed to rank artists', 
                                    user=user, selected=country)

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
                                    user=user, selected=country)

        return render_template('index.html', found=True, urls=urls, 
                                countries=countries, user=user, selected=country)



if __name__ == '__main__':
    app.run()