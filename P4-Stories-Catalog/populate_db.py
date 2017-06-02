from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Story

"""
    Populate the genre table
"""

engine = create_engine('sqlite:///StoriesDatabase.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()
# Make this an autocommit session instead of having every other line say commit
session.autocommit = True

# user = User(name='Aditya', email='aditya@cybersapien.xyz')
# session.add(user)
# session.commit()

usr = session.query(User).filter_by(name='Aditya').one()

story1 = Story(title="The Big Question", author_id=usr.id)

session.add(story1)

