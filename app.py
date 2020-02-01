from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS
from models import setup_db, Actor, Movie
from auth import AuthError, requires_auth

DEFAULT_OFFSET = 1
DEFAULT_LIMIT = 30
# Get a list of paginated questions
def paginate_response(request, selection):
  offset = request.args.get('offset', DEFAULT_OFFSET, type=int)
  limit = request.args.get('limit', DEFAULT_LIMIT, type=int)
  start =  (offset - 1) * limit
  end = start + limit

  formatted_selection = [item.format() for item in selection]
  paginated_selection = formatted_selection[start:end]

  return paginated_selection

def create_app(test_config=None):
  # Create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  #  GET Actors
  #  ----------------------------------------------------------------
  @app.route('/actors')
  @requires_auth('get:actors')
  def get_actors(jwt):
    try:
      return jsonify({
        'success': True,
        'actors': paginate_response(request, Actor.query.order_by(Actor.id).all())
      })
    except:
      abort(422)

  #  GET Movies
  #  ----------------------------------------------------------------
  @app.route('/movies')
  @requires_auth('get:movies')
  def get_movies(jwt):
    return jsonify({
      'success': True,
      'movies': paginate_response(request, Movie.query.order_by(Movie.id).all())
    })

  #  POST Actors
  #  ----------------------------------------------------------------
  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actors')
  def create_actor(jwt):
    body = request.json
    name = body.get('name', None)
    age = body.get('age', None)
    gender = body.get('gender', None)

    # Abort 400 if the name in the request matches any of the saved actor names
    if name in list(map(Actor.get_name, Actor.query.all())):
      abort(400, 'This name is already taken. Please provide a new name and try again.')

    # Abort 400 if any fields are missing
    if any(arg is None for arg in [name, age, gender]) or '' in [name, age, gender]:
      abort(400, 'name, age and gender are required fields.')

    # Create and insert a new actor
    new_actor = Actor(name=name, age=age, gender=gender)
    new_actor.insert()

    # Return the newly created actor
    return jsonify({
      'success': True,
      'actors': [Actor.query.get(new_actor.id).format()]
    })

  #  POST Movies
  #  ----------------------------------------------------------------
  @app.route('/movies', methods=['POST'])
  @requires_auth('post:movies')
  def create_movie(jwt):
    body = request.json
    title = body.get('title', None)
    release_date = body.get('release_date', None)

    # Abort 400 if the title in the request matches any of the saved movie titles
    if title in list(map(Movie.get_title, Movie.query.all())):
      abort(400, 'This title is already taken. Please provide a new title and try again.')

    # Abort 400 if any fields are missing
    if any(arg is None for arg in [title, release_date]) or '' in [title, release_date]:
      abort(400, 'title and release_date are required fields.')

    # Create and insert a new movie
    new_movie = Movie(title=title, release_date=release_date)
    new_movie.insert()

    # Return the newly created movie
    return jsonify({
      'success': True,
      'movies': [Movie.query.get(new_movie.id).format()]
    })

  #  PATCH Actors
  #  ----------------------------------------------------------------
  @app.route('/actors/<actor_id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def update_actor(jwt, actor_id):
    actor = Actor.query.get(actor_id)

    # Abort 404 if the actor was not found
    if actor is None:
      abort(404)

    body = request.json
    name = body.get('name', None)
    age = body.get('age', None)
    gender = body.get('gender', None)

    # Abort 400 if any fields are missing
    if any(arg is None for arg in [name, age, gender]) or '' in [name, age, gender]:
      abort(400, 'name, age and gender are required fields.')

    # Update the actor with the requested fields
    actor.name = name
    actor.age = age
    actor.gender = gender
    actor.update()

    # Return the updated actor
    return jsonify({
      'success': True,
      'actors': [Actor.query.get(actor_id).format()]
    })

  #  PATCH Movies
  #  ----------------------------------------------------------------
  @app.route('/movies/<movie_id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def update_movie(jwt, movie_id):
    movie = Movie.query.get(movie_id)

    # Abort 404 if the movie was not found
    if movie is None:
      abort(404)

    body = request.json
    title = body.get('title', None)
    release_date = body.get('release_date', None)

    # Abort 400 if any fields are missing
    if any(arg is None for arg in [title, release_date]) or '' in [title, release_date]:
      abort(400, 'title and release_date are required fields.')

    # Update the movie with the requested fields
    movie.title = title
    movie.release_date = release_date
    movie.update()

    # Return the updated movie
    return jsonify({
      'success': True,
      'movies': [Movie.query.get(movie_id).format()]
    })

  #  DELETE Actors
  #  ----------------------------------------------------------------
  @app.route('/actors/<actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(jwt, actor_id):
    actor = Actor.query.get(actor_id)

    # Abort 404 if the actor was not found
    if actor is None:
      abort(404)

    # Delete the actor
    actor.delete()

    return jsonify({
      'success': True,
      'delete': actor_id
    })

  #  DELETE Movies
  #  ----------------------------------------------------------------
  @app.route('/movies/<movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(jwt, movie_id):
    movie = Movie.query.get(movie_id)

    # Abort 404 if the movie was not found
    if movie is None:
      abort(404)

    # Delete the movie
    movie.delete()

    return jsonify({
      'success': True,
      'delete': movie_id
    })

  #----------------------------------------------------------------------------#
  # Error Handling.
  #----------------------------------------------------------------------------#
  # Unprocessable Entity
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unable to process your request. Please try again later."
    }), 422

  # Not Found
  @app.errorhandler(404)
  def not_found_error(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Resource not found."
    }), 404

  # Bad Request
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": str(error)
    }), 400

  # AuthError exceptions raised by the @requires_auth(permission) decorator method
  @app.errorhandler(AuthError)
  def auth_error(auth_error):
    return jsonify({
      "success": False,
      "error": auth_error.status_code,
      "message": auth_error.error['description']
    }), auth_error.status_code

  return app

app = create_app()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)