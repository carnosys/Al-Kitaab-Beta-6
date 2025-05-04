# index.py
from flask import Flask
from flask_mail import Mail
from config import Config
from views import views_bp
from surah_page import surah_page_bp
from email_notifications import mail, start_notification_service
from scheduler import start_streak_scheduler
from loader import load_surah_texts

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Mail
mail.init_app(app)

# Start the notification service
start_notification_service(app)

# Start the streak scheduler
start_streak_scheduler()

# Initialize surahs
app.config['SURAH_LIST'] = Config.load_surahs(app.root_path)

# Load Quran texts
app.config['QURAN_TEXTS'] = load_surah_texts(app.root_path)

# Register blueprints
app.register_blueprint(views_bp)
app.register_blueprint(surah_page_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
