# surah_page.py
from flask import Blueprint, render_template, abort
from loader import load_surah_texts
import logging

logger = logging.getLogger(__name__)
surah_page_bp = Blueprint('surah_page', __name__, template_folder='templates', static_folder='static', static_url_path='/static')
# load all texts
_texts = load_surah_texts(surah_page_bp.root_path)
arabic = _texts['arabic']
english_quran = _texts['english']['quran']['en.sahih']['quran']['en.sahih']
indopak = _texts['indopak']['quran']
tajweed = _texts['tajweed']['quran']

def get_text_metadata(collection, surah_id, text_key_map):
    # returns list of dicts matching surah
    return [
        {'ayah_number': v.get(text_key_map['ayah']), 'text': v.get(text_key_map['text'])}
        for v in collection.values() if v.get(text_key_map['surah'])==surah_id
    ]

@surah_page_bp.route('/surah/<int:surah_id>')
def display_surah(surah_id):
    if not arabic:
        abort(500, description="Arabic surah data missing")
    if not 1 <= surah_id <= len(arabic):
        abort(404, description="Surah not found")
    
    # Get the base surah data
    surah = arabic[surah_id-1]
    logger.debug(f"Loading surah {surah_id}: {surah['name']}")
    
    # Get translations and other texts with correct key mappings
    translation_list = []
    for key, value in english_quran.items():
        if value.get('surah') == surah_id:
            translation_list.append({
                'ayah_number': value.get('ayah'),
                'text': value.get('verse', '')
            })
    
    logger.debug(f"Found {len(translation_list)} translations for surah {surah_id}")
    logger.debug(f"Sample translation: {translation_list[0] if translation_list else 'No translations found'}")
    
    indopak_list = get_text_metadata(indopak, surah_id, {'ayah':'ayah','text':'text','surah':'surah'})
    tajweed_list = get_text_metadata(tajweed, surah_id, {'ayah':'ayah','text':'text','surah':'surah'})

    # Create a mapping of ayah numbers to their respective texts
    translation_map = {item['ayah_number']: item['text'] for item in translation_list}
    indopak_map = {item['ayah_number']: item['text'] for item in indopak_list}
    tajweed_map = {item['ayah_number']: item['text'] for item in tajweed_list}

    # Create properly ordered lists matching the Arabic verses
    ordered_translation = []
    ordered_indopak = []
    ordered_tajweed = []

    for verse in surah['verses']:
        ayah_number = verse['id']
        translation = translation_map.get(ayah_number, '')
        logger.debug(f"Ayah {ayah_number} translation: {translation}")
        
        ordered_translation.append({
            'ayah_number': ayah_number,
            'text': translation
        })
        ordered_indopak.append({
            'ayah_number': ayah_number,
            'text': indopak_map.get(ayah_number, '')
        })
        ordered_tajweed.append({
            'ayah_number': ayah_number,
            'text': tajweed_map.get(ayah_number, '')
        })

    logger.debug(f"First ordered translation: {ordered_translation[0] if ordered_translation else 'No translations'}")
    
    return render_template('pages/surahPage.html',
        surah=surah,
        surah_translation=ordered_translation,
        surah_indopak=ordered_indopak,
        surah_tajweed=ordered_tajweed
    )
