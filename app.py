from flask import Flask, render_template, request
import musiclib

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        
        user = request.form['user']
        country = request.form['country']

        try:
            artists = musiclib.get_top_100_lastfm(user)
        except:
            print('Error: invalid username?')
            return render_template('index.html')

        try:
            genres = musiclib.rank_genres(artists)
        except Exception as e:
            print('Error: failed to get genres?', e)
            return render_template('index.html')

        try:
            artistsfound = musiclib.rank_artists_by_country(genres, country)
        except Exception as e:
            print('Error: failed to rank artists', e)
            return render_template('index.html')

        urls = []
        count = 0
        for artist in artistsfound.keys():
            if count >= 10:
                break
            url = artistsfound[artist]['url'][:25] + 'embed' + artistsfound[artist]['url'][24:]
            urls.append(url)
            count += 1

        print(urls)

        return render_template('index.html', found=True, urls=urls)



if __name__ == '__main__':
    app.run()