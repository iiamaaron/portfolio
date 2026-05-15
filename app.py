from flask import Flask, request, jsonify, render_template
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message as MailMessage
from dotenv import load_dotenv
import os

#.env the bridge btw the environment it runs in
# keeping sensitive infos like passwords, API keys etc out of source code
load_dotenv() #reads .env file so secrets stays out of the code

app = Flask(__name__)

# Database  config
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
database_url = os.getenv('DATABASE_URL', 'sqlite:///portfolio.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'sslmode': 'require'},
    'pool_pre_ping': True,
    'pool_recycle': 300
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

#pulls those secret values in safely
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
mail = Mail(app)


@app.route('/')
def index():
    return render_template('index.html')

class Message(db.Model): #A table in the database
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String, nullable = False)
    message = db.Column(db.Text, nullable = False)
    #Created_at records when the message was sent, automatically
    created_at = db.Column(db.DateTime, default = db.func.now())








@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json() #reads the data coming from the frontend form
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    # Validates that all three fields are present
    if not name or not email or not message:
        return jsonify({'error': 'All fields are required!'}), 400

    try:
        # create a Message object
        new_message = Message(name=name, email=email, message=message)
        # and save it to the database
        db.session.add(new_message)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({'error': 'Could not save message'}), 500

    return jsonify({'success': 'Message received'}), 200
"""
    try:
        msg = MailMessage(
            subject = f'New message from {name}',
            sender = os.getenv('MAIL_USERNAME'),
            recipients = [os.getenv('MAIL_USERNAME')],
            body = f'Name: {name}\nEmail: {email}\n\nMessage: \n{message}'
        )
        mail.send(msg)
    except Exception as e:
        print(f"Mail error: {e}")

    return jsonify({'success': 'Message received'}), 200
"""










@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('admin.html', messages=messages)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


