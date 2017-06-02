# ORM using SQLAlchemy

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine
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
        """Serialized object for User class"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture_link': self.picture_link
        }


# The Stories are blog posts
class Story(Base):
    __tablename__ = 'story'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False, unique=True)
    content = Column(String(250))  # nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'))
    date = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now())
    author = relationship(User, cascade="delete")

    @property
    def serialize(self):
        """Serialized return object"""
        return {
            'title': self.title,
            'id': self.id,
            'date': str(self.date),
            'content': self.content,
            'author_id': self.author_id,
            'author': self.author.serialize
        }


engine = create_engine('sqlite:///StoriesDatabase.db')
Base.metadata.create_all(engine)
