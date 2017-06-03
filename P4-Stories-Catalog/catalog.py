from flask import Flask, request, redirect, url_for, flash, jsonify
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Source, Quote

app = Flask(__name__)

# Create session and connect to Database
engine = create_engine('sqlite:///QuotesDatabase.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#################################
#       JSON return points      #
#################################

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


#################################
#          HTML end points      #
#################################
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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
