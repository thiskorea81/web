from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db

import csv
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('dashboard'))
    return '로그인 실패!'

@app.route('/dashboard')
@login_required
def dashboard():
    return '환영합니다! 로그인에 성공하셨습니다.'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file_post():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join('uploads', filename))
        process_csv(os.path.join('uploads', filename))
    return redirect(url_for('index'))

def process_csv(filepath):
    with open(filepath, 'r') as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            username, password = row[0], row[1]
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
        db.session.commit()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

with app.app_context():
    db.create_all()
