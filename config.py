# config.py
import os
import json

class Config:
    SECRET_KEY = 'session1'

    # MySQL Database configuration
    DB = {
        'host': 'localhost',
        'user': 'al_kitab_user',
        'password': 'yourpassword',
        'database': 'Al_Kitab'
    }

    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'tahanafis4000@gmail.com'
    MAIL_PASSWORD = 'zzzgxheshpezcabk'  # App Password without spaces
    MAIL_DEFAULT_SENDER = 'tahanafis4000@gmail.com'

    # Load Quran surahs metadata once
    @classmethod
    def load_surahs(cls, root_path):
        path = os.path.join(root_path, 'quran_surahs.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

