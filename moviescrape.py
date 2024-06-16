from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

base_url = "https://www.rottentomatoes.com/browse/movies_at_home/"

genres = {
    'ALL': 'all', 
    'ACTION': 'action',
    'ADVENTURE': 'adventure',
    'ANIMATION': 'animation',
    'ANIME': 'anime',
    'BIOGRAPHY': 'biography',
    'COMEDY': 'comedy',
    'CRIME': 'crime',
    'DOCUMENTARY': 'documentary',
    'DRAMA': 'drama',
    'ENTERTAINMENT': 'entertainment',
    'FAITH & SPIRITUALITY': 'faith_and_spirituality',
    'GAME SHOW': 'game_show',
    'LGBTQ+': 'lgbtq',
    'HEALTH & WELLNESS': 'health_and_wellness',
    'HISTORY': 'history',
    'HOLIDAY': 'holiday',
    'HORROR': 'horror',
    'HOUSE & GARDEN': 'house_and_garden',
    'KIDS & FAMILY': 'kids_and_family',
    'MUSIC': 'music',
    'MUSICAL': 'musical',
    'MYSTERY & THRILLER': 'mystery_and_thriller',
    'NATURE': 'nature',
    'NEWS': 'news',
    'REALITY': 'reality',
    'ROMANCE': 'romance',
    'SCI-FI': 'sci_fi',
    'SHORT': 'short',
    'SOAP': 'soap',
    'SPECIAL INTEREST': 'special_interest',
    'SPORTS': 'sports',
    'STAND-UP': 'stand_up',
    'TALK SHOW': 'talk_show',
    'TRAVEL': 'travel',
    'VARIETY': 'variety',
    'WAR': 'war',
    'WESTERN': 'western'
}

def scrape_movies(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    movies = soup.find_all("div", class_="flex-container")
    tlist = []
    tlink = []
    meterlist = []
    desclist = []
    imageList = []

    for movie in movies:
        title = movie.find("span", class_="p--small").text.strip()
        link = movie.a["href"]
        full_link = "https://www.rottentomatoes.com" + link
        tlist.append(title)
        tlink.append(full_link)

        image_tag = movie.find("rt-img", class_="posterImage")
        if image_tag:
            image_url = image_tag.get("src")  
        imageList.append(image_url)

        movie_page = requests.get(full_link).text
        movie_soup = BeautifulSoup(movie_page, "html.parser")

        tmeter = movie_soup.find("rt-text", {"size":"1.375"}).text
        meterlist.append(tmeter)
        
        code = movie_soup.find_all("div", class_="media-scorecard no-border")
        for films in code:     
            description = films.find("drawer-more", {"slot":"description"}).find("rt-text", {"slot":"content"}).text.strip()            
        desclist.append(description)
        
    data = {
        "Movie Title": tlist,
        "Movie link": tlink,
        "Image": imageList,
        "Tomato Meter": meterlist,
        "Movie Description": desclist
    }
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    genres_list = list(genres.keys()) 

    if request.method == 'POST':
        selected_genre = request.form['genre']
        if selected_genre.lower() == 'all':
            return redirect(url_for('index')) 
        else:
            return redirect(url_for('movies_by_genre', genre=selected_genre))

    selected_genre = request.args.get('genre', 'ALL')
    page = int(request.args.get('page', 1))

    if selected_genre == 'ALL':
        url = base_url + f"sort:popular?page={page}"
    else:
        genre_url = genres.get(selected_genre.upper(), 'all')
        url = base_url + f"genres:{genre_url}~sort:popular?page={page}"

    data = scrape_movies(url)

    return render_template('index.html', data=data, genres=genres_list, selected_genre=selected_genre, page=page)

@app.route('/movies/<genre>')
def movies_by_genre(genre):
    genres_list = list(genres.keys()) 
    page = int(request.args.get('page', 1))

    if genre == 'ALL':
        url = base_url + f"sort:popular?page={page}"
    else:
        genre_url = genres.get(genre.upper(), 'all')
        url = base_url + f"genres:{genre_url}~sort:popular?page={page}"

    data = scrape_movies(url)
    return render_template('index.html', data=data, genres=genres_list, selected_genre=genre, page=page)

if __name__ == '__main__':
    app.run(debug=True)
