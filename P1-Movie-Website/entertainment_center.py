import json
import requests

import fresh_tomatoes
from media import Movie

api_base_url = 'https://yts.ag/api/v2/list_movies.json?minimum_rating=8&sort_by=rating'

''' Get data from YTS api and parse the movie details to Movie objects '''
data = requests.get(api_base_url)  # using the requests library for making HTTP requests for movie data
contents = data.content
parsedJSON = json.loads(contents) # parse the contents from JSON to a dynamic object
movies = (parsedJSON['data']['movies'])

myMovies = []
for movie in movies:
    currentMovie = Movie(movie['title'], movie['summary'], movie['medium_cover_image'], movie['yt_trailer_code'])
    myMovies.append(currentMovie)

fresh_tomatoes.open_movies_page(myMovies)
