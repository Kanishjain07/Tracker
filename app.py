from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate
from datetime import datetime
import pymysql
pymysql.install_as_MySQLdb()
from models import db, User, Workout, Hydration, Symptom, Period

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/fitness_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        height = request.form['height']
        weight = request.form['weight']
        service = request.form['service']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(name=name, gender=gender, dob=datetime.strptime(dob, '%Y-%m-%d'), height=height, weight=weight, service=service, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration Successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['name']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Failed. Please check your name and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    hydrations = Hydration.query.filter_by(user_id=current_user.id).all()
    symptoms = Symptom.query.filter_by(user_id=current_user.id).all()
    periods = Period.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', workouts=workouts, hydrations=hydrations, symptoms=symptoms, periods=periods)

@app.route('/add_workout', methods=['POST', 'GET'])
@login_required
def add_workout():
    if request.method == 'POST':
        workout_type = request.form['workout_type']
        duration = request.form['duration']
        new_workout = Workout(user_id=current_user.id, workout_type=workout_type, duration=duration)
        db.session.add(new_workout)
        db.session.commit()
        flash('Workout added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_workout.html')

@app.route('/add_hydration', methods=['POST', 'GET'])
@login_required
def add_hydration():
    if request.method == 'POST':
        water_intake = request.form['water_intake']
        new_hydration = Hydration(user_id=current_user.id, water_intake=water_intake)
        db.session.add(new_hydration)
        db.session.commit()
        flash('Hydration added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_hydration.html')

@app.route('/add_symptom', methods=['POST', 'GET'])
@login_required
def add_symptom():
    if request.method == 'POST':
        description = request.form['description']
        new_symptom = Symptom(user_id=current_user.id, description=description)
        db.session.add(new_symptom)
        db.session.commit()
        flash('Symptom added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_symptom.html')

@app.route('/add_period', methods=['POST', 'GET'])
@login_required
def add_period():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        new_period = Period(user_id=current_user.id, start_date=datetime.strptime(start_date, '%Y-%m-%d'), end_date=datetime.strptime(end_date, '%Y-%m-%d'))
        db.session.add(new_period)
        db.session.commit()
        flash('Period details added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_period.html')

if __name__ == "__main__":
    from os import environ
    from app import app
    app.run(debug=False, host='0.0.0.0', port=int(environ.get("PORT", 5000)))