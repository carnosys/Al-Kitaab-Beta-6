# surah_page.py
import os
import json
import logging
import requests
from flask import Blueprint, render_template, abort

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

surah_page_bp = Blueprint('surah_page', __name__, template_folder='templates')

# Translation IDs from Al-Quran Cloud API
TRANSLATIONS = {
    'english': 'en.sahih',  # English Sahih International
    'urdu': 'ur.ahmedali',  # Urdu Ahmed Ali
    'hindi': 'hi.hindi'     # Hindi
}

# Determine paths relative to this blueprint
base = surah_page_bp.root_path
arabic_path = os.path.join(base, 'quran.json')
english_path = os.path.join(base, 'en.sahih.json')
indopak_path = os.path.join(base, 'indopak.json')
tajweed_path = os.path.join(base, 'tajweed.json')

def fetch_translation(surah_id, translation_id):
    """Fetch translation from Al-Quran Cloud API"""
    try:
        url = f"https://api.alquran.cloud/v1/surah/{surah_id}/{translation_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['data']['ayahs']
    except Exception as e:
        logger.error(f"Error fetching translation {translation_id} for surah {surah_id}: {e}")
        return []

# Load Arabic text
with open(arabic_path, 'r', encoding='utf-8') as f:
    surahs = json.load(f)
    logger.debug(f"Loaded Arabic Surahs from {arabic_path}")

# Load English translation
with open(english_path, 'r', encoding='utf-8') as f:
    sahih_translation = json.load(f)
    logger.debug(f"Loaded English translation from {english_path}")

# Initialize optional scripts
indopak = {"quran": {}}
tajweed = {"quran": {}}

# Load Indopak if available
try:
    with open(indopak_path, 'r', encoding='utf-8') as f:
        indopak = json.load(f)
        logger.debug(f"Loaded Indopak script from {indopak_path}")
except FileNotFoundError:
    logger.warning(f"Indopak file not found at {indopak_path}, skipping.")
except json.JSONDecodeError as e:
    logger.error(f"Error decoding Indopak JSON: {e}")

# Load Tajweed if available
try:
    with open(tajweed_path, 'r', encoding='utf-8') as f:
        tajweed = json.load(f)
        logger.debug(f"Loaded Tajweed script from {tajweed_path}")
except FileNotFoundError:
    logger.warning(f"Tajweed file not found at {tajweed_path}, skipping.")
except json.JSONDecodeError as e:
    logger.error(f"Error decoding Tajweed JSON: {e}")

@surah_page_bp.route('/surah/<int:surah_id>')
def display_surah(surah_id):
    # Validate
    if not 1 <= surah_id <= len(surahs):
        logger.error(f"Invalid surah_id: {surah_id}")
        abort(404, description="Surah not found")

    # Fetch translations from API
    translations = {}
    for lang, translation_id in TRANSLATIONS.items():
        translations[lang] = fetch_translation(surah_id, translation_id)

    # English verses
    translation = []
    for verse in sahih_translation["quran"]["en.sahih"].values():
        if verse["surah"] == surah_id:
            translation.append({"ayah_number": verse["ayah"], "text": verse["verse"]})

    # Indopak verses
    indopak_list = []
    for verse in indopak.get("quran", {}).values():
        if verse.get("surah") == surah_id:
            indopak_list.append({"ayah_number": verse.get("ayah"), "text": verse.get("text")})

    # Tajweed verses
    tajweed_list = []
    for verse in tajweed.get("quran", {}).values():
        if verse.get("surah") == surah_id:
            tajweed_list.append({"ayah_number": verse.get("ayah"), "text": verse.get("text")})

    # Pad missing verses
    total_verses = len(surahs[surah_id-1]["verses"])
    while len(indopak_list) < total_verses:
        indopak_list.append({"ayah_number": len(indopak_list)+1, "text": ""})
    while len(tajweed_list) < total_verses:
        tajweed_list.append({"ayah_number": len(tajweed_list)+1, "text": ""})

    return render_template(
        'surahPage.html',
        surah=surahs[surah_id-1],
        surah_translation=translation,
        surah_indopak=indopak_list,
        surah_tajweed=tajweed_list,
        translations=translations
    )
