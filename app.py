from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, ParkingLot, ParkingSpot, Reservation
from database import init_database
from datetime import datetime

app = Flask(__name__)

#Configuration settings
app.config['SECRET_KEY'] = 'citypark2025secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///citypark.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
init_database(app)

@app.route('/')
def landing():
    return render_template('landing.html')



@app.route('/login', methods=['GET', 'POST']) #url with specific http method gives specific 
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Automatically detect user type and redirect accordingly
            if user.is_admin:
                session['user_type'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            else:
                session['user_type'] = 'user'
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        phone = request.form.get('phone', '')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return render_template('register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered')
            return render_template('register.html')
        
        new_user = User(
            username=username, 
            email=email, 
            full_name=full_name, 
            password=password, 
            phone=phone,
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')
#Admin routes
#Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    lots = ParkingLot.query.all()
    users = User.query.filter_by(is_admin=False).all()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    
    return render_template('admin_dashboard.html', 
                         lots=lots, 
                         users=users, 
                         total_spots=total_spots, 
                         occupied_spots=occupied_spots)

@app.route('/admin/manage_lots')
def manage_lots():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    lots = ParkingLot.query.all()
    return render_template('manage_lots.html', lots=lots)


@app.route('/admin/view_spots/<int:lot_id>')
def view_spots(lot_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    # Get spot details with current reservations
    spot_details = []
    for spot in spots:
        active_reservation = Reservation.query.filter_by(
            spot_id=spot.id, 
            status='active'
        ).first()
        
        spot_info = {
            'spot': spot,
            'reservation': active_reservation,
            'user': active_reservation.user if active_reservation else None
        }
        spot_details.append(spot_info)
    
    return render_template('view_spots.html', lot=lot, spot_details=spot_details)
# Admin Reservations means viewing all reservations/parkings made by users
@app.route('/admin/reservations')
def view_all_reservations():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))

    reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('admin_reservations.html', reservations=reservations)


@app.route('/admin/create_lot', methods=['POST'])
def create_lot():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    location_name = request.form['location_name']
    price_per_hour = float(request.form['price_per_hour'])
    address = request.form['address']
    pin_code = request.form['pin_code']
    max_spots = int(request.form['max_spots'])
    
    new_lot = ParkingLot(
        prime_location_name=location_name,
        price_per_hour=price_per_hour,
        address=address,
        pin_code=pin_code,
        maximum_number_of_spots=max_spots
    )
    
    db.session.add(new_lot)
    db.session.commit()
    
    # Create parking spots automatically
    for i in range(1, max_spots + 1):
        spot = ParkingSpot(lot_id=new_lot.id, spot_number=i, status='A')
        db.session.add(spot)
    
    db.session.commit()
    flash('Parking lot created successfully!')
    return redirect(url_for('manage_lots'))

@app.route('/admin/edit_lot', methods=['POST'])
def edit_lot():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    lot_id = int(request.form['lot_id'])
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Update lot details
    lot.prime_location_name = request.form['location_name']
    lot.price_per_hour = float(request.form['price_per_hour'])
    lot.address = request.form['address']
    lot.pin_code = request.form['pin_code']
    
    new_max_spots = int(request.form['max_spots'])
    old_max_spots = lot.maximum_number_of_spots
    
    # Handle spot count changes
    if new_max_spots != old_max_spots:
        if new_max_spots > old_max_spots:
            # Add new spots
            for i in range(old_max_spots + 1, new_max_spots + 1):
                new_spot = ParkingSpot(lot_id=lot.id, spot_number=i, status='A')
                db.session.add(new_spot)
        elif new_max_spots < old_max_spots:
            # Remove spots (only if they're not occupied)
            spots_to_remove = ParkingSpot.query.filter(
                ParkingSpot.lot_id == lot_id,
                ParkingSpot.spot_number > new_max_spots
            ).all()
            
            # Check if any spots to be removed are occupied
            occupied_spots_to_remove = [spot for spot in spots_to_remove if spot.status == 'O']
            if occupied_spots_to_remove:
                flash(f'Cannot reduce spots to {new_max_spots}. Spots {[s.spot_number for s in occupied_spots_to_remove]} are occupied.')
                return redirect(url_for('manage_lots'))
            
            # Remove the empty spots
            for spot in spots_to_remove:
                db.session.delete(spot)
    
    # Update the lot's max spots
    lot.maximum_number_of_spots = new_max_spots
    
    db.session.commit()
    flash('Parking lot updated successfully!')
    return redirect(url_for('manage_lots'))

@app.route('/admin/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    
    if occupied_spots > 0:
        flash('Cannot delete lot with occupied spots!')
        return redirect(url_for('manage_lots'))
    
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!')
    return redirect(url_for('manage_lots'))

@app.route('/admin/charts')
def admin_charts():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    lots = ParkingLot.query.all()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    
    # Get recent reservations for trends (last 10)
    recent_reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).limit(10).all()
    
    return render_template('admin_charts.html', 
                         lots=lots, 
                         total_spots=total_spots, 
                         occupied_spots=occupied_spots,
                         recent_reservations=recent_reservations)
# User Dashboard
#User Routes
@app.route('/user/dashboard')
def user_dashboard():
    if session.get('user_type') != 'user':
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    active_reservation = Reservation.query.filter_by(user_id=user_id, status='active').first()
    lots = ParkingLot.query.all()
    
    return render_template('user_dashboard.html', 
                         active_reservation=active_reservation, 
                         lots=lots)

@app.route('/user/book_spot/<int:lot_id>', methods=['GET', 'POST'])
def book_spot(lot_id):
    if session.get('user_type') != 'user':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        user_id = session['user_id']
        vehicle_number = request.form['vehicle_number'].strip().upper()
        
        # Check if user already has an active reservation
        existing_reservation = Reservation.query.filter_by(user_id=user_id, status='active').first()
        if existing_reservation:
            flash('You already have an active reservation!')
            return redirect(url_for('user_dashboard'))
        
        # Find first available spot
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            flash('No available spots in this parking lot!')
            return redirect(url_for('user_dashboard'))
        
        # Create reservation with vehicle number
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=user_id,
            vehicle_number=vehicle_number,
            parking_timestamp=datetime.now(),
            status='active'
        )
        
        # Update spot status
        available_spot.status = 'O'
        
        db.session.add(reservation)
        db.session.commit()
        
        flash(f'Spot booked successfully for vehicle {vehicle_number}!')
        return redirect(url_for('user_dashboard'))
    
    return render_template('book_spot_form.html', lot=lot)

@app.route('/user/release_spot/<int:reservation_id>')
def release_spot(reservation_id):
    if session.get('user_type') != 'user':
        return redirect(url_for('login'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != session['user_id']:
        flash('Unauthorized access!')
        return redirect(url_for('user_dashboard'))
    
    # Calculate parking duration and cost
    leaving_time = datetime.now()
    parking_duration = leaving_time - reservation.parking_timestamp
    
    # Calculate exact hours parked(time difference and price per unit time)
    hours_parked = parking_duration.total_seconds() / 3600
    
    # Get lot price per hour
    lot = reservation.parking_spot.parking_lot
    
    # Calculate cost: time difference × price per unit time
    cost = hours_parked * lot.price_per_hour
    
    # Update reservation
    reservation.leaving_timestamp = leaving_time
    reservation.parking_cost = round(cost, 2)
    reservation.status = 'completed'
    
    # Update spot status
    reservation.parking_spot.status = 'A'
    
    db.session.commit()
    
    flash(f'Spot released! Total cost: ₹{reservation.parking_cost}')
    return redirect(url_for('user_dashboard'))

@app.route('/user/history')
def user_history():
    if session.get('user_type') != 'user':
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()
    
    return render_template('user_history.html', reservations=reservations)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)