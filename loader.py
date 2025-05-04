# loader.py
from flask import Blueprint, current_app
import os
import json
from config import Config

def inject_surahs(app):
    app.config['SURAH_LIST'] = Config.load_surahs(app.root_path)

def load_surah_texts(root_path):
    """Load Quran texts from different sources (Arabic, English, Indopak, Tajweed)"""
    texts = {
        'arabic': [],
        'english': {'quran': {'en.sahih': {}}},
        'indopak': {'quran': {}},
        'tajweed': {'quran': {}}
    }
    
    # Load Arabic text
    arabic_path = os.path.join(root_path, 'quran.json')
    if os.path.exists(arabic_path):
        with open(arabic_path, 'r', encoding='utf-8') as f:
            texts['arabic'] = json.load(f)
    
    # Load English translation
    english_path = os.path.join(root_path, 'en.sahih.json')
    if os.path.exists(english_path):
        with open(english_path, 'r', encoding='utf-8') as f:
            texts['english']['quran']['en.sahih'] = json.load(f)
    
    # Load Indopak script
    indopak_path = os.path.join(root_path, 'indopak.json')
    if os.path.exists(indopak_path):
        with open(indopak_path, 'r', encoding='utf-8') as f:
            texts['indopak']['quran'] = json.load(f)
    
    # Load Tajweed text
    tajweed_path = os.path.join(root_path, 'tajweed.json')
    if os.path.exists(tajweed_path):
        with open(tajweed_path, 'r', encoding='utf-8') as f:
            texts['tajweed']['quran'] = json.load(f)
    
    return texts
