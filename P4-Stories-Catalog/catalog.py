from flask import Flask, request, redirect, url_for, flash, jsonify
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Source, Quote, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

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
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture_link=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

"""
    authentication end points for Google Plus oAuth2
"""
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate the state token
    if request.args.get('state') != login_session['state']:
        


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
    return render_template('quotes.html', quotes=quotes, sources=sources)


@app.route('/source/<int:src_id>/quotes')
@app.route('/source/<int:src_id>')
def quotes_for_source(src_id):
    source = session.query(Source).filter_by(id=src_id).one()
    sources = session.query(Source).all()
    quotes = session.query(Quote).filter_by(source_id=src_id).all()
    return render_template('quotes.html', quotes=quotes, source=source, sources=sources)


@app.route('/source/new', methods=['GET', 'POST'])
def newSource():
    if request.method == 'POST':
        newSRC = Source(name=request.form['source_name'])
        session.add(newSRC)
        session.commit()
        flash('New source %s Added Successfully!' % newSRC.name)
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('newSource.html', sources=sources)

@app.route('/source/edit/<int:src_id>', methods=['GET', 'POST'])
def edit_source(src_id):
    source = session.query(Source).filter_by(id=src_id).one()
    if request.method == 'POST':
        source.name = request.form['source_name']
        session.add(source)
        session.commit()
        flash("Source Updated Successfully!")
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('editSource.html', source=source, sources=sources)


@app.route('/source/delete/<int:src_id>', methods=['GET', 'POST'])
def delete_source(src_id):
    source = session.query(Source).filter_by(id=src_id).one()
    if request.method == 'POST':
        session.delete(source)
        session.commit()
        flash("Source successfully deleted")
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('deleteConfirm.html', source=source, sources=sources, quote=None)


@app.route('/quote/new', methods=['GET', 'POST'])
def new_quote():
    if request.method == 'POST':
        newQt = Quote(title=request.form['q_title'],
                      content=request.form['q_content'],
                      source_id=request.form['src_id'])
        session.add(newQt)
        session.commit()
        flash('New Quote %s Added Successfully!' % newQt.title)
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('newQuote.html', sources=sources)


@app.route('/quote/edit/<int:q_id>', methods=['GET', 'POST'])
def edit_quote(q_id):
    quote = session.query(Quote).filter_by(id=q_id).one()
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
        return render_template('editQuote.html', quote=quote, sources=sources)


@app.route('/quote/delete/<int:q_id>', methods=['GET', 'POST'])
def delete_quote(q_id):
    quote = session.query(Quote).filter_by(id=q_id).one()
    if request.method == 'POST':
        session.delete(quote)
        session.commit()
        flash("Quote Successfully Deleted!")
        return redirect(url_for('all_quotes'))
    else:
        sources = session.query(Source).all()
        return render_template('deleteConfirm.html', quote=quote, sources=sources, source=None)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
