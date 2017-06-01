class Movie:
    """    The Movie class stores the title, brief, poster and trailer of an instance of a movie
    """

    def __init__(self, title, brief, poster, trailer_id):
        self.title = title
        self.brief = brief
        self.poster_image_url = poster
        self.yt_link = trailer_id
