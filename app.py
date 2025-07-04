from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'my_super_secret_key'

# Конфігурація бази даних
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Конфігурація пошти (заміни на свої)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='nalyvaikoigor546@gmail.com',
    MAIL_PASSWORD='your_app_password'  # має бути App Password!
)
mail = Mail(app)

# Модель апартаменту
class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)

# Модель бронювання
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'))
    date = db.Column(db.String(20))

# Головна
@app.route('/')
def index():
    apartments = Apartment.query.all()
    return render_template('index.html', apartments=apartments)

# Перегляд апартаменту
@app.route('/apartments/<int:apartment_id>')
def room(apartment_id):
    apartment = Apartment.query.get_or_404(apartment_id)
    return render_template('room.html', apartment=apartment)

# Бронювання апартаменту
@app.route('/book/<int:apartment_id>', methods=['GET', 'POST'])
def book(apartment_id):
    apartment = Apartment.query.get_or_404(apartment_id)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        date = request.form['date']
        booking = Booking(name=name, email=email, apartment_id=apartment_id, date=date)
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('booking.html', apartment=apartment)

# Додавання нового апартаменту
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        new_apartment = Apartment(name=name, description=description, price=price)
        db.session.add(new_apartment)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

# Зворотний зв'язок
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        msg = Message(
            subject=f"📩 Нове повідомлення від {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']],
            body=f"Від: {name} <{email}>\n\n{message}"
        )
        try:
            mail.send(msg)
            flash('✅ Повідомлення успішно надіслано!')
        except Exception as e:
            print(f"❌ Помилка при надсиланні: {e}")
            flash('⚠️ Сталася помилка під час надсилання. Спробуйте ще раз.')
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        if booking_id:
            booking = Booking.query.get(int(booking_id))
            if booking:
                db.session.delete(booking)
                db.session.commit()
                flash('❌ Бронювання видалено!')
        return redirect(url_for('bookings'))

    all_bookings = Booking.query.all()
    bookings_data = []
    for b in all_bookings:
        apartment = Apartment.query.get(b.apartment_id)
        bookings_data.append({
            'id': b.id,
            'name': b.name,
            'email': b.email,
            'date': b.date,
            'apartment_name': apartment.name if apartment else '—'
        })
    return render_template('bookings.html', bookings=bookings_data)

@app.route('/edit/<int:apartment_id>', methods=['GET', 'POST'])
def edit(apartment_id):
    apartment = Apartment.query.get_or_404(apartment_id)
    if request.method == 'POST':
        apartment.name = request.form['name']
        apartment.description = request.form['description']
        apartment.price = float(request.form['price'])
        db.session.commit()
        flash('✅ Апартамент оновлено!')
        return redirect(url_for('index'))
    return render_template('edit.html', apartment=apartment)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        apartment_id = request.form.get('apartment_id')
        action = request.form.get('action')
        if apartment_id and action == 'delete':
            apartment = Apartment.query.get(int(apartment_id))
            if apartment:
                db.session.delete(apartment)
                db.session.commit()
                flash('❌ Апартамент видалено!')
        return redirect(url_for('manage'))

    apartments = Apartment.query.all()
    return render_template('manage.html', apartments=apartments)
@app.route('/stats')
def stats():
    stats_data = db.session.query(
        Apartment.name,
        db.func.count(Booking.id)
    ).join(Booking).group_by(Apartment.id).all()

    return render_template('stats.html', stats=stats_data)



# Ініціалізація бази з демо-даними
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Apartment.query.first():
            demo1 = Apartment(name='Квартира з видом', description='Простора квартира біля парку', price=1300)
            demo2 = Apartment(name='Сучасна студія', description='У самому серці Львова', price=1100)
            db.session.add_all([demo1, demo2])
            db.session.commit()
    app.run(debug=True)
