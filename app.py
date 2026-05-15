from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message as MailMessage
from dotenv import load_dotenv
import os

#.env the bridge btw the environment it runs in
# keeping sensitive infos like passwords, API keys etc out of source code
load_dotenv() #reads .env file so secrets stays out of the code

app = Flask(__name__)

# Database  config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

#pulls those secret values in safely
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db = SQLAlchemy(app)

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
        return jsonify({'error': 'All fields are required!'})

    # create a Message object
    new_message = Message(name=name, email=email, message=message)
    # and save it to the database
    db.session.add(new_message)
    db.session.commit()

    msg = MailMessage(
        subject = f'New message from {name}',
        sender = os.getenv('MAIL_USERNAME'),
        recipients = [os.getenv('MAIL_USERNAME')],
        body = f'Name: {name}\nEmail: {email}\n\nMessage: \n{message}'
    )
    mail.send(msg)
    return jsonify({'success': 'Message received'}), 200

mail = Mail(app)

if __name__ == '__main__':
    app.run(debug=True)

