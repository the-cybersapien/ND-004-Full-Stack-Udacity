from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Quote, Source

"""
    Populate the genre table
"""

engine = create_engine('sqlite:///QoutesDatabase.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()
# Make this an autocommit session instead of having every other line say commit

user = User(name='Aditya', email='aditya@cybersapien.xyz')
session.add(user)
session.commit()

user = User(name='CBRSPN', email='cybersapien.97@gmail.com')
session.add(user)
session.commit()

usr1 = session.query(User).filter_by(name='Aditya').one()
usr2 = session.query(User).filter_by(name='CBRSPN').one()

source = Source(name='Doctor Who', user_id=usr2.id)
session.add(source)
session.commit()

source = Source(name='Arrow', user_id=usr1.id)
session.add(source)
session.commit()

source = Source(name='The Flash', user_id=usr2.id)
session.add(source)
session.commit()

src1 = session.query(Source).filter_by(name='Doctor Who').one()
src2 = session.query(Source).filter_by(name='Arrow').one()
src3 = session.query(Source).filter_by(name='The Flash').one()

qoute1 = Quote(title="The Question",
               content="Silence will fall when the Question will be asked! The oldest question "
                       "in the universe! DOCTOR WHO? DOCTOR WHO?",
               author_id=usr1.id,
               source_id=src1.id)
session.add(qoute1)
session.commit()

qoute2 = Quote(title="Mad Man with a Box!",
               content="Amy Pond, there's something you better understand about me, "
                       "because it's important and one day, your life may depend on it. "
                       "I am Definitely a madman with a box!",
               author_id=usr1.id,
               source_id=src1.id)
session.add(qoute2)
session.commit()

qoute3 = Quote(title="Everybody Dies",
               content="Everybody knows that everybody dies. And nobody knows it like the "
                       "Doctor. But I do think that all the skies of all the worlds might "
                       "just turn dark if he ever, for one moment accepts it!",
               author_id=usr1.id,
               source_id=src1.id)
session.add(qoute3)
session.commit()

qoute4 = Quote(title="Interogation",
               content="Felicity: \"How do you normally get information from "
                       "criminals?\"\nOliver: \"I find the person, and then I put the fear "
                       "of God into them until they talk. But we can try your way.\"",
               author_id=usr2.id,
               source_id=src2.id)
session.add(qoute4)
session.commit()

qoute5 = Quote(title="Trap",
               content="Didn't anyone ever tell you? There's one thing you never put in a trap. If you're smart, "
                       "if you value your continued existance, if you have any plans about seeing tomorrow, "
                       "there is one thing, you never EVER put into a trap! ME",
               author_id=usr2.id,
               source_id=src1.id)
session.add(qoute5)

qoute6 = Quote(title="Locomotive",
               content="Life is locomotion. If you're not moving, you're not living. But there comes a time, "
                       "when you've got to stop running away from things and you've got to start running towards "
                       "something. You've got to forge ahead. Keep Moving. Even if your path isn't lit, TRUST that "
                       "you'll find your way.",
               author_id=usr2.id,
               source_id=src3.id)
session.add(qoute6)
session.commit()
session.flush()
