from app import *
from datetime import datetime


with app.app_context():
    db.create_all()

    # Check if there are any movies in the database
    if not MovieHall.query.first():
        # Add some movies
        # initial_movies = [
        #     Movie(name='The Shawshank Redemption', category='Drama', arrival_date=datetime.strptime('1994-09-23', '%Y-%m-%d'), rating=9.3),
        #     Movie(name='The Godfather', category='Crime', arrival_date=datetime.strptime('1972-03-24', '%Y-%m-%d'), rating=9.2),
        #     Movie(name='The Dark Knight', category='Action', arrival_date=datetime.strptime('2008-07-18', '%Y-%m-%d'), rating=9.0),
        #     Movie(name='Pulp Fiction', category='Crime', arrival_date=datetime.strptime('1994-10-14', '%Y-%m-%d'), rating=8.9),
        #     Movie(name='Forrest Gump', category='Drama', arrival_date=datetime.strptime('1994-07-06', '%Y-%m-%d'), rating=8.8),
        # ]
        
        # db.session.bulk_save_objects(initial_movies)
        # db.session.commit()
        initial_halls = [
            MovieHall(name='Cineplex 1', location='Downtown', capacity=200, screen_type='IMAX'),
            MovieHall(name='Cineplex 2', location='Suburb', capacity=150, screen_type='3D'),
            MovieHall(name='Grand Cinema', location='City Center', capacity=300, screen_type='Standard'),
            MovieHall(name='Movie Palace', location='Uptown', capacity=250, screen_type='4DX'),
        ]
    
        db.session.bulk_save_objects(initial_halls)
        db.session.commit()