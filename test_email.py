from flask import Flask
from flask_mail import Mail, Message
from config import Config

# Create a Flask app instance
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)

def send_test_email():
    try:
        with app.app_context():
            # Print configuration for debugging
            print("Email Configuration:")
            print(f"Server: {app.config['MAIL_SERVER']}")
            print(f"Port: {app.config['MAIL_PORT']}")
            print(f"Username: {app.config['MAIL_USERNAME']}")
            print(f"Use TLS: {app.config['MAIL_USE_TLS']}")
            
            # Create message
            msg = Message(
                subject="Test Email - Quran Reading Reminder",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=['tahanafis0@gmail.com'],
                body="Assalamu Alaikum,\n\nThis is a test email from Al-Kitab. It's time to read the Quran and reflect upon its teachings.\n\nBest regards,\nAl-Kitab Team"
            )
            
            # Send email
            mail.send(msg)
            print("Test email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    send_test_email() 