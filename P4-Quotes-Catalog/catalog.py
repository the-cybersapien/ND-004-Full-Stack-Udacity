import json
import random
import string

import httplib2
import requests
from flask import Flask, request, redirect, url_for, flash, jsonify
from flask import make_response
from flask import render_template
from flask import session as login_session
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Source, Quote, User

app = Flask(__name__)

# G-Plus Client ID for the Application
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APP_NAME = 'Quotes for Fun'

# Create session and connect to Database
engine = create_engine('sqlite:///QuotesDatabase.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

"""
    User Helper Functions
"""


def create_user(login_session):
    new_user = User(name=login_session['username'], email=login_session['email'], picture_link=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/login')
def show_login():
    sources = session.query(Source).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', login_session=login_session, sources=sources, STATE=state)


"""
    authentication end points for Google Plus oAuth2
"""


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate the state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code=code)

        # Check the validity of the access token
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(str(h.request(url, 'GET')[1]))

        # Check for error in the response code
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is for the intended user
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(json.dumps("Token's user ID doesn't match the given user's ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for the app
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("Token's client ID does not match  app's."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')

        # If the user is already connected, flash a message and return a success 200 code
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token for later use
        login_session['credentials'] = credentials
        login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']

        user_id = get_user_id(login_session['email'])

        if not user_id:
            user_id = create_user(login_session)

        login_session['user_id'] = user_id

        user = get_user_info(user_id)
        output = 'Login Successful!'
        flash("You are now logged in!")
        return output

    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.', 401))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current User not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, method='GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        flash('Successfully Logged out!')
        return redirect(url_for('all_quotes'))
    else:
        response = make_response(jsonify(result), 200)
        response.headers['Content-Type'] = 'text/plain'
        return response


"""
    JSON end-points for the Application
"""


# JSON page for all sources
@app.route('/sources/JSON')
def sourcesJSON():
    sources = session.query(Source).all()
    return jsonify(Sources=[source.serialize for source in sources])


# JSON page for specific source
@app.route('/sources/<int:src_id>/JSON')
def sourceJSON(src_id):
    source = session.query(Source).filter_by(id=src_id).one()
    return jsonify(source.serialize)


# JSON for all quotes
@app.route('/quotes/JSON')
def quotesJSON():
    quotes = session.query(Quote).all()
    return jsonify(quotes=[quote.serialize for quote in quotes])


# JSON for quotes from a specific source
@app.route('/sources/<int:src_id>/quotes/JSON')
def quotesFromSource(src_id):
    quotes = session.query(Quote).filter_by(source_id=src_id).all()
    source = session.query(Source).filter_by(id=src_id).one()
    return jsonify(Source=source.serialize, quotes=[q.serialize_without_source for q in quotes])


# JSON for a specific quote
@app.route('/quotes/<int:q_id>/JSON')
def quoteJSON(q_id):
    quote = session.query(Quote).filter_by(id=q_id).one()
    return jsonify(Quote=quote.serialize)


"""
    HTML end points for the app
    Since the app is designed in a manner that sources are always displayed in the Nav Bar,
    All the render template functions will be having a sources parameter containing a list of sources
"""


@app.route('/')
@app.route('/quotes')
def all_quotes():
    quotes = session.query(Quote).all()
    sources = session.query(Source).all()
    return render_template('quotes.html', login_session=login_session, quotes=quotes, sources=sources)


@app.route('/source/<int:src_id>/quotes')
@app.route('/source/<int:src_id>')
def quotes_for_source(src_id):
    source = session.query(Source).filter_by(id=src_id).one()
    sources = session.query(Source).all()
    quotes = session.query(Quote).filter_by(source_id=src_id).all()
    return render_template('quotes.html', login_session=login_session, quotes=quotes, source=source, sources=sources)


@app.route('/source/new', methods=['GET', 'POST'])
def new_source():
    if 'username' not in login_session:
        flash("You need to login before adding a new Source")
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        new_src = Source(name=request.form['source_name'],
                         user_id=login_session['user_id'])
        session.add(new_src)
        session.commit()
        flash('New source %s Added Successfully!' % new_src.name)
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('newSource.html', login_session=login_session, sources=sources)


@app.route('/source/edit/<int:src_id>', methods=['GET', 'POST'])
def edit_source(src_id):
    if 'username' not in login_session:
        flash("You need to login before making a change")
        return redirect(url_for('show_login'))
    source = session.query(Source).filter_by(id=src_id).one()
    if source.user_id != login_session['user_id']:
        flash("You are not authorized to make this change!")
        return redirect(url_for('all_quotes'))
    if request.method == 'POST':
        source.name = request.form['source_name']
        session.add(source)
        session.commit()
        flash("Source Updated Successfully!")
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('editSource.html', login_session=login_session, source=source, sources=sources)


@app.route('/source/delete/<int:src_id>', methods=['GET', 'POST'])
def delete_source(src_id):
    if 'username' not in login_session:
        flash("You need to login before making a change")
        return redirect(url_for('show_login'))
    source = session.query(Source).filter_by(id=src_id).one()
    if source.user_id != login_session['user_id']:
        flash("You are not authorized to make this change!")
        return redirect(url_for('all_quotes'))
    if request.method == 'POST':
        session.delete(source)
        session.commit()
        flash("Source successfully deleted")
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('deleteConfirm.html', login_session=login_session, source=source, sources=sources, quote=None)


@app.route('/quote/new', methods=['GET', 'POST'])
def new_quote():
    if 'username' not in login_session:
        flash("You need to login before adding a new Quote")
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        new_qt = Quote(title=request.form['q_title'],
                       content=request.form['q_content'],
                       author_id=login_session['user_id'],
                       source_id=request.form['src_id'])
        session.add(new_qt)
        session.commit()
        flash('New Quote %s Added Successfully!' % new_qt.title)
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('newQuote.html', login_session=login_session, sources=sources)


@app.route('/quote/edit/<int:q_id>', methods=['GET', 'POST'])
def edit_quote(q_id):
    if 'username' not in login_session:
        flash("You need to login before making a change")
        return redirect(url_for('show_login'))
    quote = session.query(Quote).filter_by(id=q_id).one()
    if quote.author_id != login_session['user_id']:
        flash("You are not authorized to make this change!")
        return redirect(url_for('all_quotes'))
    if request.method == 'POST':
        if request.form['q_title']:
            quote.title = request.form['q_title']
        if request.form['q_content']:
            quote.content = request.form['q_content']
        if request.form['src_id']:
            quote.source_id = request.form['src_id']
        session.add(quote)
        session.commit()
        flash('Quote updated successfully!')
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('editQuote.html', login_session=login_session, quote=quote, sources=sources)


@app.route('/quote/delete/<int:q_id>', methods=['GET', 'POST'])
def delete_quote(q_id):
    if 'username' not in login_session:
        flash("You need to login before making a change")
        return redirect(url_for('show_login'))
    quote = session.query(Quote).filter_by(id=q_id).one()
    if quote.author_id != login_session['user_id']:
        flash("You are not authorized to make this change!")
        return redirect(url_for('all_quotes'))
    if request.method == 'POST':
        session.delete(quote)
        session.commit()
        flash("Quote Successfully Deleted!")
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('deleteConfirm.html', login_session=login_session, quote=quote, sources=sources, source=None)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
