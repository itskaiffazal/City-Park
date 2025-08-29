from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(35), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    

    #This means: "One user can have many reservations" 
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    #parking_spots: Links this lot to all its individual parking spots

    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
#cascade='all, delete-orphan': If we delete a parking lot, delete all its spots too
class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # A=Available, O=Occupied
    
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.now)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed
    vehicle_number = db.Column(db.String(20), nullable=False)