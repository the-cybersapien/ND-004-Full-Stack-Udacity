from flask import Flask, request, redirect, url_for, flash, jsonify
from flask import render_template
from database_setup import Base, User, Source, Quote
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)

# Create session and connect to Database
engine = create_engine('sqlite:///QoutesDatabase.db')
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


# JSON for all qoutes
@app.route('/qoutes/JSON')
def qoutesJSON():
    qoutes = session.query(Quote).all()
    return jsonify(Qoutes=[qoute.serialize for qoute in qoutes])

# JSON for qoutes from a specific source
@app.route('/sources/<int:src_id>/qoutes/JSON')
def qoutesFromSource(src_id):
    qoutes = session.query(Quote).filter_by(source_id=src_id).all()
    source = session.query(Source).filter_by(id=src_id).one()
    return jsonify(Source=source.serialize,Qoutes=[q.serializeWOSource for q in qoutes])

# JSON for a specific qoute
@app.route('/qoutes/<int:q_id>/JSON')
def qouteJSON(q_id):
    qoute = session.query(Quote).filter_by(id=q_id).one()
    return jsonify(Qoute=qoute.serialize)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
