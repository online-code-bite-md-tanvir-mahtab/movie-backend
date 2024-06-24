import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from  datetime import datetime
# from model.user import *
# import model.user


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviedb.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    sessions = db.relationship('Session', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone
        }


class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    logged_in = db.Column(db.Boolean, nullable=False, default=False)
    # user = db.relationship('User', backref=db.backref('session', uselist=False))
    

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    arrival_date = db.Column(db.Date, nullable=False)
    rating = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"Movie(name={self.name}, category={self.category}, arrival_date={self.arrival_date}, rating={self.rating})"
    

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    release_date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    overview = db.Column(db.Text, nullable=True)
    popularity = db.Column(db.Float, nullable=True)
    vote_count = db.Column(db.Integer, nullable=True)
    vote_average = db.Column(db.Float, nullable=True)
    original_language = db.Column(db.String(50), nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    poster_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Movie {self.title}>'

    
class MovieHall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    screen_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"MovieHall(name={self.name}, location={self.location}, capacity={self.capacity}, screen_type={self.screen_type})"



# Define the Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey('movie_hall.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    movie = db.relationship('Movie', backref=db.backref('bookings', lazy=True))
    hall = db.relationship('MovieHall', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f"Booking(user_name={self.user_name}, movie_id={self.movie_id}, hall_id={self.hall_id}, seats={self.seats})"



class MovieRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100))
    rating = db.Column(db.Float)
    release_date = db.Column(db.Date)

    def __repr__(self):
        return f"MovieRequest(name='{self.name}', genre='{self.genre}', rating={self.rating}, release_date={self.release_date})"


@app.before_request
def create_database():
    with app.app_context():
        db.create_all()



@app.route('/')
def home():
    return "Welcome to the api"


@app.route('/signup', methods=['POST', 'GET'])
def createUser():
    if request.method == 'POST':
        # Ensure that all required keys are present in the JSON payload
        if all(key in request.json for key in ['name', 'email', 'phone', 'password']):
            userName = request.json['name']
            userEmail = request.json['email']
            userPhone = request.json['phone']
            userPassword = request.json['password']
            
            # Check if the email or phone number is already registered
            existing_user = User.query.filter(
                (User.email == userEmail) | (User.phone == userPhone)
            ).first()
            if existing_user:
                return jsonify({'message': 'Email or phone number already registered'}), 400
            
            # Create a new user object
            new_user = User(username=userName, email=userEmail, phone=userPhone, password=userPassword)
            
            # Add the user to the database session and commit the transaction
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            
            # Return a success message with the newly created user's details
            return jsonify({'message': 'User created successfully'}), 200
        else:
            # Return a bad request error if required keys are missing
            return jsonify({'message': 'Missing required fields in JSON payload'}), 400
    else:
        # Handle GET requests if needed
        return jsonify({'message': 'GET request received. This endpoint only accepts POST requests.'}), 405

    
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.json
        useremail = data.get('email')
        password = data.get('password')

        # Query the database to find a user with the provided email
        user = User.query.filter_by(email=useremail).first()

        # Check if the user exists and the password matches
        if user and user.password == password:
            # Update existing session data or create a new session
            with app.app_context():
                existing_session = Session.query.filter_by(user_id=user.id).first()
                if existing_session:
                    existing_session.logged_in = True
                else:
                    new_session = Session(user_id=user.id, logged_in=True)
                    db.session.add(new_session)
                db.session.commit()

            # Store user ID in session
            session['user_id'] = user.id

            return jsonify({'message': 'Login successful', 'userId': user.id}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401



@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        user_id = request.json.get('user_id')
        print(user_id)

        with app.app_context():
            user_session = Session.query.filter_by(user_id=user_id, logged_in=True).first()
            if user_session:
                user_session.logged_in = False
                db.session.commit()

        session.pop('user_id', None)
        return jsonify({'message': 'Logout successful'}), 200
    else:
        return jsonify({'message': 'No user is logged in'}), 400

    

@app.route('/is_logged_in', methods=['POST'])
def is_logged_in():
    if request.method == 'POST':
        user_id = request.json.get('user_id')
        
        if not user_id:
            return jsonify({'message': 'User ID not provided', 'logged_in': False}), 400
        
        session_data = Session.query.filter_by(user_id=user_id).first()
        
        if session_data and session_data.logged_in:
            return jsonify({'message': 'User is logged in', 'logged_in': True}), 200
        else:
            return jsonify({'message': 'User is not logged in', 'logged_in': False}), 200
    else:
        return jsonify({'message': 'Method not allowed. Use POST instead.'}), 405



@app.route('/movies', methods=['GET'])
def get_movies():
    # Query the database to retrieve all movies
    movies = Movie.query.all()
    
    # Convert the movie objects to a list of dictionaries
    movies_list = []
    for movie in movies:
        movie_dict = {
            'id': movie.id,
            'name': movie.name,
            'category': movie.category,
            'arrival_date': movie.arrival_date.strftime('%Y-%m-%d'),
            'rating': movie.rating
        }
        movies_list.append(movie_dict)
    
    # Return the movie data in JSON format
    return jsonify(movies_list)


@app.route('/movie_halls', methods=['GET'])
def get_movie_halls():
    # Query the database to retrieve all movie halls
    halls = MovieHall.query.all()

    # Convert the movie hall objects to a list of dictionaries
    halls_list = []
    for hall in halls:
        hall_dict = {
            'id': hall.id,
            'name': hall.name,
            'location': hall.location,
            'capacity': hall.capacity,
            'screenType': hall.screen_type
        }
        halls_list.append(hall_dict)

    # Return the movie halls as a JSON response
    return jsonify({'movie_halls': halls_list})



@app.route('/book_seat', methods=['POST'])
def book_seat():
    data = request.json
    movie_id = data.get('movie_id')
    hall_id = data.get('hall_id')
    user_id = data.get('user_id')
    seats = data.get('seats')

    if not all([movie_id, hall_id, user_id, seats]):
        return jsonify({'message': 'Missing required fields'}), 400

    hall = MovieHall.query.get(hall_id)
    if not hall:
        return jsonify({'message': 'Invalid hall ID'}), 404

    booked_seats = db.session.query(db.func.sum(Booking.seats)).filter_by(hall_id=hall_id).scalar() or 0
    available_seats = hall.capacity - booked_seats

    if seats > available_seats:
        return jsonify({'message': f'Not enough seats available. Only {available_seats} seats left.'}), 400

    booking = Booking(movie_id=movie_id, hall_id=hall_id, user_id=user_id, seats=seats)
    with app.app_context():
        db.session.add(booking)
        db.session.commit()

    return jsonify({'message': 'Booking successful'}), 200

@app.route('/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    bookings_list = []
    for booking in bookings:
        booking_dict = {
            'id': booking.id,
            'movie_id': booking.movie_id,
            'hall_id': booking.hall_id,
            'user_id': booking.user_id ,
            'seats': booking.seats,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d')
        }
        bookings_list.append(booking_dict)
    return jsonify({'bookings': bookings_list})



@app.route('/available_seats/<int:hall_id>', methods=['GET'])
def available_seats(hall_id):
    hall = MovieHall.query.get(hall_id)
    if not hall:
        return jsonify({'message': 'Invalid hall ID'}), 404

    booked_seats = db.session.query(db.func.sum(Booking.seats)).filter_by(hall_id=hall_id).scalar() or 0
    available_seats = hall.capacity - booked_seats

    return jsonify({'available_seats': available_seats})


@app.route('/movie_requests', methods=['POST'])
def create_movie_request():
    data = request.json
    existing_request = MovieRequest.query.filter_by(
        name=data['name'],
        genre=data.get('genre'),
        rating=data.get('rating'),
        release_date=datetime.strptime(data['release_date'], '%Y-%m-%d').date()
    ).first()

    if existing_request:
        return jsonify({"message": "Movie request already exists"}), 409

    new_request = MovieRequest(
        name=data['name'],
        genre=data.get('genre'),
        rating=data.get('rating'),
        release_date=datetime.strptime(data['release_date'], '%Y-%m-%d').date()
    )
    with app.app_context():
        db.session.add(new_request)
        db.session.commit()

    return jsonify({"message": "Movie request created successfully"}), 201

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({'message': 'User not found'}), 404
    
    
    
@app.route('/add_movie', methods=['POST'])
def add_movie():
    data = request.json

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        release_date = datetime.strptime(data['Release_Date'], '%Y-%m-%d').date()
        title = data['Title']
        overview = data['Overview']
        popularity = float(data['Popularity']) if data['Popularity'] else None
        vote_count = int(data['Vote_Count']) if data['Vote_Count'] else None
        vote_average = float(data['Vote_Average']) if data['Vote_Average'] else None
        original_language = data['Original_Language']
        genre = data['Genre']
        poster_url = data['Poster_Url']

        new_movie = Movies(
            release_date=release_date,
            title=title,
            overview=overview,
            popularity=popularity,
            vote_count=vote_count,
            vote_average=vote_average,
            original_language=original_language,
            genre=genre,
            poster_url=poster_url
        )
        with app.app_context():
            db.session.add(new_movie)
            db.session.commit()

        return jsonify({"message": "Movie added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/allmovies', methods=['GET'])
def get_all_movies():
    movies = Movies.query.all()
    return jsonify([movie.to_dict() for movie in movies]), 200


if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)