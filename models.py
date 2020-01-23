
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#  Actor Model
#  ----------------------------------------------------------------
class Actor(db.Model):
  __tablename__ = 'Movie'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  age = db.Column(db.Integer, nullable=False)
  gender = db.Column(db.String, nullable=False)

  '''
  get_name()
    name of the Actor
  '''
  def get_name(self):
    return self.name

  '''
  insert()
    inserts a new model into a database
    the model must have a unique name
    EXAMPLE
      actor = Actor(name=name, age=age, gender=gender)
      actor.insert()
  '''
  def insert(self):
    db.session.add(self)
    db.session.commit()

  '''
  update()
    updates a model into a database
    the model must exist in the database
    EXAMPLE
      actor = Actor.query.get(actor_id)
      actor.name = 'Nate'
      actor.update()
  '''
  def update(self):
    db.session.commit()

  '''
  delete()
    deletes a model from the database
    the model must exist in the database
    EXAMPLE
      actor = Actor.query.get(actor_id)
      actor.delete()
  '''
  def delete(self):
    db.session.delete(self)
    db.session.commit()

#  Movie Model
#  ----------------------------------------------------------------
class Movie(db.Model):
  __tablename__ = 'Movie'

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String, nullable=False)
  release_date = db.Column(db.DateTime(), default=datetime.utcnow)

  '''
  get_title()
    title of the Movie
  '''
  def get_title(self):
    return self.title

  '''
  insert()
    inserts a new model into a database
    the model must have a unique title
    EXAMPLE
      movie = Movie(title=title, release_date=release_date)
      movie.insert()
  '''
  def insert(self):
    db.session.add(self)
    db.session.commit()

    '''
  update()
    updates a model into a database
    the model must exist in the database
    EXAMPLE
      movie = Movie.query.get(movie_id)
      movie.title = 'New Adventure'
      movie.update()
  '''
  def update(self):
    db.session.commit()

  '''
  delete()
    deletes a model from the database
    the model must exist in the database
    EXAMPLE
      movie = Movie.query.get(movie_id)
      movie.delete()
  '''
  def delete(self):
    db.session.delete(self)
    db.session.commit()
