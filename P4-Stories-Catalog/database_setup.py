# ORM using SQLAlchemy

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# User Entity with attributes
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture_link = Column(String(250))

    @property
    def serialize(self):
        """
        Serialized object for User class.
        Since this is used for JSON data, not passing the email or Picture here
        """
        return {
            'id': self.id,
            'name': self.name
        }


class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    user_id = Column(String(250), ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'user': self.user.serialize
        }


# The Quotes are blog posts
class Quote(Base):
    __tablename__ = 'story'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False, unique=True)
    content = Column(String(250))  # nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'))
    source_id = Column(Integer, ForeignKey('source.id'))
    date = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now())
    # Adding cascade delete since the qoutes are defined by their author and source
    author = relationship(User, cascade='delete')
    source = relationship(Source, cascade='delete')

    @property
    def serialize(self):
        """General Serialized JSON object with all the data"""
        return {
            'title': self.title,
            'id': self.id,
            'date': str(self.date),
            'content': self.content,
            'author': self.author.serialize,
            'source': self.source.serialize
        }

    @property
    def serialize_without_source(self):
        """Serialized JSON without the source to prevent redundancy"""
        return {
            'title': self.title,
            'id': self.id,
            'date': str(self.date),
            'content': self.content,
            'author': self.author.serialize
        }


engine = create_engine('sqlite:///QoutesDatabase.db')
Base.metadata.create_all(engine)
