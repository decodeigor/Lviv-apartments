from app import db, Apartment, Booking
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db.init_app(app)

with app.app_context():
    db.create_all()
    print("База даних створена 🎉")
