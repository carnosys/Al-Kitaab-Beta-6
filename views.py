# views.py
from flask import Blueprint, render_template, redirect, url_for, request, session, abort, jsonify, current_app
from config import Config
from services import (
    get_user_by_username, get_user_by_username_or_email,
    create_user, get_last_seen, update_user_basic_info,
    insert_user_goals, init_user_streak, update_last_seen as svc_update_last_seen,
    start_reading_session, end_reading_session, get_db_connection,
    get_user_by_email
)
from loader import load_surah_texts
import os
import json

views_bp = Blueprint('views', __name__, static_folder='static', static_url_path='/static')

def get_surah_metadata(surahs, surah_no):
    # support dict with string keys or list
    if isinstance(surahs, dict):
        return surahs.get(str(surah_no))
    if isinstance(surahs, list) and 1 <= surah_no <= len(surahs):
        return surahs[surah_no-1]
    return None

@views_bp.route('/')
def home_page():
    if 'username' not in session:
        return redirect(url_for('views.login'))
    
    username = session['username']
    last = get_last_seen(username)
    last_info = None
    current_streak = 0
    
    # Get user's current streak
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT us.current_streak
                FROM users u
                JOIN user_streaks us ON u.user_id = us.user_id
                WHERE u.username = %s
            """, (username,))
            streak_info = cursor.fetchone()
            if streak_info:
                current_streak = streak_info['current_streak']
        finally:
            cursor.close()
            conn.close()
    
    if last and last['last_seen_surah'] and last['last_seen_ayah']:
        surahs = current_app.config['SURAH_LIST']
        meta = get_surah_metadata(surahs, last['last_seen_surah'])
        if meta:
            last_info = {
                'surah_number': last['last_seen_surah'],
                'surah_name': meta.get('name'),
                'surah_name_arabic': meta.get('arabic_name'),
                'ayah_number': last['last_seen_ayah']
            }
    
    return render_template(
        'pages/index.html',
        surahs=current_app.config['SURAH_LIST'],
        username=username,
        last_seen_info=last_info,
        current_streak=current_streak
    )

@views_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']
        if action == 'signin':
            user = get_user_by_username(username)
            if user and user['password'] == password:
                session['username'] = user['username']
                return redirect(
                    url_for('views.user_info')
                    if user['is_first_login']
                    else url_for('views.home_page')
                )
            return render_template('auth/login.html', error="Invalid credentials")
        else:
            existing = get_user_by_username_or_email(username, email)
            if existing:
                return render_template('auth/login.html', error="Username or Email exists")
            create_user(username, email, password)
            session['username'] = username
            return redirect(url_for('views.user_info'))
    return render_template('auth/login.html')

@views_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.login'))

@views_bp.route('/user-info', methods=['GET','POST'])
def user_info():
    if 'username' not in session:
        return redirect(url_for('views.login'))
    if request.method == 'POST':
        gender = request.form.get('gender')
        lang = request.form.get('preferred_language')
        country = request.form.get('country')
        script = request.form.get('preferred_script')
        verses = request.form.get('verses_per_session')
        window_start = request.form.get('window_start')
        window_end = request.form.get('window_end')
        freq = request.form.get('reminder_freq')
        hrs = request.form.get('interval_hours') or 0
        mins = request.form.get('interval_minutes') or 0
        interval = int(hrs) * 60 + int(mins) if freq == 'custom' else None

        user = get_user_by_username(session['username'])
        if not user:
            abort(404)
        uid = user['user_id']
        update_user_basic_info(uid, gender, country, script, lang)
        insert_user_goals(uid, verses, window_start, window_end, freq, interval)
        init_user_streak(uid)
        return redirect(url_for('views.home_page'))
    return render_template('auth/user-info.html')

@views_bp.route('/progress-and-analytics')
def progress():
    return render_template('pages/progressAndAnalysitcs.html')

@views_bp.route('/settings')
def settings():
    return render_template('pages/settings.html')

@views_bp.route('/profile-settings', methods=['GET', 'POST'])
def profile_settings():
    if 'username' not in session:
        return redirect(url_for('views.login'))
    
    user = get_user_by_username(session['username'])
    if not user:
        return redirect(url_for('views.login'))
    
    if request.method == 'POST':
        # Verify password first
        password = request.form.get('password')
        if password != user['password']:
            return render_template('auth/profileSettings.html', 
                                user=user,
                                error="Incorrect password")
        
        # Get form data
        gender = request.form.get('gender')
        preferred_language = request.form.get('preferred_language')
        country = request.form.get('country')
        email = request.form.get('email')
        
        # Check if email is already taken by another user
        if email != user['user_email']:
            existing_user = get_user_by_email(email)
            if existing_user and existing_user['user_id'] != user['user_id']:
                return render_template('auth/profileSettings.html',
                                    user=user,
                                    error="Email is already taken")
        
        # Update user information
        conn = get_db_connection()
        if not conn:
            return render_template('auth/profileSettings.html',
                                user=user,
                                error="Database error")
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users 
                SET gender = %s,
                    preffered_languge = %s,
                    country = %s,
                    user_email = %s
                WHERE user_id = %s
            """, (gender, preferred_language, country, email, user['user_id']))
            conn.commit()
            
            # Update user object with new values
            user['gender'] = gender
            user['preffered_languge'] = preferred_language
            user['country'] = country
            user['user_email'] = email
            
            return render_template('auth/profileSettings.html',
                                user=user,
                                success="Settings updated successfully")
        except Exception as e:
            print(f"Error updating user settings: {e}")
            return render_template('auth/profileSettings.html',
                                user=user,
                                error="Failed to update settings")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('auth/profileSettings.html', user=user)

@views_bp.route('/update-last-seen', methods=['POST'])
def update_last_seen_handler():
    if 'username' not in session:
        return jsonify(status='error', message='Not logged in'), 401
    data = request.get_json()
    sid, aid = data.get('surah_id'), data.get('ayah_id')
    if not sid or not aid:
        return jsonify(status='error', message='Missing data'), 400
    success = svc_update_last_seen(session['username'], sid, aid)
    return jsonify(status='success' if success else 'error'), (200 if success else 500)

@views_bp.route('/start-session', methods=['POST'])
def start_session():
    if 'username' not in session:
        return jsonify(status='error', message='Not logged in'), 401
    
    data = request.get_json()
    start_ayah = data.get('start_ayah')
    if not start_ayah:
        return jsonify(status='error', message='Missing start ayah'), 400
    
    user = get_user_by_username(session['username'])
    if not user:
        return jsonify(status='error', message='User not found'), 404
    
    session_id = start_reading_session(user['user_id'], start_ayah)
    if not session_id:
        return jsonify(status='error', message='Failed to start session'), 500
    
    return jsonify(status='success', session_id=session_id)

@views_bp.route('/end-session', methods=['POST'])
def end_session():
    if 'username' not in session:
        return jsonify(status='error', message='Not logged in'), 401
    
    data = request.get_json()
    session_id = data.get('session_id')
    end_ayah = data.get('end_ayah')
    verses_read = data.get('verses_read')
    duration = data.get('duration')
    
    if not all([session_id, end_ayah, verses_read, duration]):
        return jsonify(status='error', message='Missing required data'), 400
    
    success = end_reading_session(session_id, end_ayah, verses_read, duration)
    if not success:
        return jsonify(status='error', message='Failed to end session'), 500
    
    return jsonify(status='success')

@views_bp.route('/api/get-streak')
def get_streak():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database error'})
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get user_id from username
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Get current streak
        cursor.execute("""
            SELECT current_streak 
            FROM user_streaks 
            WHERE user_id = %s
        """, (user['user_id'],))
        streak = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'current_streak': streak['current_streak'] if streak else 0
        })
    except Exception as e:
        print(f"Error fetching streak: {e}")
        return jsonify({'success': False, 'error': 'Server error'})
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/account-settings', methods=['GET', 'POST'])
def account_settings():
    if 'username' not in session:
        return redirect(url_for('views.login'))
    
    user = get_user_by_username(session['username'])
    if not user:
        return redirect(url_for('views.login'))
    
    if request.method == 'POST':
        # Verify password first
        password = request.form.get('password')
        if password != user['password']:
            return render_template('auth/account-settings.html', 
                                user=user,
                                error="Incorrect password")
        
        # Get form data
        gender = request.form.get('gender')
        preferred_language = request.form.get('preferred_language')
        country = request.form.get('country')
        email = request.form.get('email')
        
        # Check if email is already taken by another user
        if email != user['user_email']:
            existing_user = get_user_by_email(email)
            if existing_user and existing_user['user_id'] != user['user_id']:
                return render_template('auth/account-settings.html',
                                    user=user,
                                    error="Email is already taken")
        
        # Update user information
        conn = get_db_connection()
        if not conn:
            return render_template('auth/account-settings.html',
                                user=user,
                                error="Database error")
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users 
                SET gender = %s,
                    preffered_languge = %s,
                    country = %s,
                    user_email = %s
                WHERE user_id = %s
            """, (gender, preferred_language, country, email, user['user_id']))
            conn.commit()
            
            # Update user object with new values
            user['gender'] = gender
            user['preffered_languge'] = preferred_language
            user['country'] = country
            user['user_email'] = email
            
            return render_template('auth/account-settings.html',
                                user=user,
                                success="Settings updated successfully")
        except Exception as e:
            print(f"Error updating user settings: {e}")
            return render_template('auth/account-settings.html',
                                user=user,
                                error="Failed to update settings")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('auth/account-settings.html', user=user)

@views_bp.route('/goal-settings', methods=['GET', 'POST'])
def goal_settings():
    if 'username' not in session:
        return redirect(url_for('views.login'))
    
    user = get_user_by_username(session['username'])
    if not user:
        abort(404)
    
    if request.method == 'POST':
        verses = request.form.get('verses_per_session')
        window_start = request.form.get('window_start')
        window_end = request.form.get('window_end')
        freq = request.form.get('reminder_freq')
        hrs = request.form.get('interval_hours') or 0
        mins = request.form.get('interval_minutes') or 0
        interval = int(hrs) * 60 + int(mins) if freq == 'custom' else None
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # Update user_goals table
                cursor.execute("""
                    UPDATE user_goals 
                    SET verses_per_session = %s,
                        window_start = %s,
                        window_end = %s,
                        reminder_freq = %s,
                        reminder_interval_minutes = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (verses, window_start, window_end, freq, interval, user['user_id']))
                
                conn.commit()
                return render_template('auth/goal-settings.html', user=user, success="Goal settings updated successfully!")
            except Exception as e:
                conn.rollback()
                return render_template('auth/goal-settings.html', user=user, error="Failed to update goal settings. Please try again.")
            finally:
                cursor.close()
                conn.close()
        else:
            return render_template('auth/goal-settings.html', user=user, error="Database connection error. Please try again.")
    
    # For GET request, fetch current goal settings
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT verses_per_session, window_start, window_end, 
                       reminder_freq, reminder_interval_minutes
                FROM user_goals
                WHERE user_id = %s
            """, (user['user_id'],))
            goal_settings = cursor.fetchone()
            
            if goal_settings:
                user.update(goal_settings)
        finally:
            cursor.close()
            conn.close()
    
    return render_template('auth/goal-settings.html', user=user)

@views_bp.route('/bookmarks-and-notes')
def bookmarks_and_notes():
    if 'username' not in session:
        return redirect(url_for('views.login'))
    
    user = get_user_by_username(session['username'])
    if not user:
        return redirect(url_for('views.login'))
    
    conn = get_db_connection()
    if not conn:
        return render_template('pages/bookmarks_and_notes.html', bookmarks=[], notes=[])
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all bookmarks for the user
        cursor.execute("""
            SELECT b.bookmark_id, b.verse_id, b.bookmark_note, b.created_at
            FROM bookmarks b
            WHERE b.user_id = %s
            ORDER BY b.created_at DESC
        """, (user['user_id'],))
        bookmarks = cursor.fetchall()
        
        # Get all notes for the user
        cursor.execute("""
            SELECT an.note_id, an.verse_id, an.note_text, an.created_at
            FROM additional_notes an
            WHERE an.user_id = %s
            ORDER BY an.created_at DESC
        """, (user['user_id'],))
        notes = cursor.fetchall()
        
        # Load Quran data
        texts = load_surah_texts(current_app.root_path)
        arabic = texts['arabic']
        
        # Load surah metadata
        surahs_path = os.path.join(current_app.root_path, 'quran_surahs.json')
        with open(surahs_path, 'r', encoding='utf-8') as f:
            surahs_metadata = json.load(f)
        
        # Enrich bookmarks with verse and surah information
        enriched_bookmarks = []
        for bookmark in bookmarks:
            verse_id = bookmark['verse_id']
            
            # Find the surah and ayah number
            surah_number = 1
            ayah_number = verse_id
            for surah in arabic:
                if ayah_number <= len(surah['verses']):
                    break
                ayah_number -= len(surah['verses'])
                surah_number += 1
            
            # Get surah information
            surah = arabic[surah_number-1]
            verse = next((v for v in surah['verses'] if v['id'] == ayah_number), None)
            
            if verse:
                # Get surah metadata
                surah_meta = surahs_metadata[str(surah_number)]
                enriched_bookmarks.append({
                    'bookmark_id': bookmark['bookmark_id'],
                    'verse_id': bookmark['verse_id'],
                    'bookmark_note': bookmark['bookmark_note'],
                    'created_at': bookmark['created_at'],
                    'surah_number': surah_number,
                    'surah_name': surah_meta['name'],
                    'surah_name_arabic': surah_meta['arabic_name'],
                    'ayah_number': ayah_number,
                    'verse_text': verse['text']
                })

        # Enrich notes with verse and surah information
        enriched_notes = []
        for note in notes:
            verse_id = note['verse_id']
            
            # Find the surah and ayah number
            surah_number = 1
            ayah_number = verse_id
            for surah in arabic:
                if ayah_number <= len(surah['verses']):
                    break
                ayah_number -= len(surah['verses'])
                surah_number += 1
            
            # Get surah information
            surah = arabic[surah_number-1]
            verse = next((v for v in surah['verses'] if v['id'] == ayah_number), None)
            
            if verse:
                # Get surah metadata
                surah_meta = surahs_metadata[str(surah_number)]
                enriched_notes.append({
                    'note_id': note['note_id'],
                    'verse_id': note['verse_id'],
                    'note_text': note['note_text'],
                    'created_at': note['created_at'],
                    'surah_number': surah_number,
                    'surah_name': surah_meta['name'],
                    'surah_name_arabic': surah_meta['arabic_name'],
                    'ayah_number': ayah_number,
                    'verse_text': verse['text']
                })
        
        return render_template('pages/bookmarks_and_notes.html', 
                             bookmarks=enriched_bookmarks,
                             notes=enriched_notes)
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/add-bookmark', methods=['POST'])
def add_bookmark():
    if 'username' not in session:
        return jsonify(status='error', message='Not logged in'), 401
    
    data = request.get_json()
    verse_id = data.get('verse_id')
    note = data.get('note')
    
    if not verse_id:
        return jsonify(status='error', message='Missing verse ID'), 400
    
    user = get_user_by_username(session['username'])
    if not user:
        return jsonify(status='error', message='User not found'), 404
    
    conn = get_db_connection()
    if not conn:
        return jsonify(status='error', message='Database error'), 500
    
    cursor = conn.cursor()
    try:
        # Check if bookmark already exists
        cursor.execute("""
            SELECT bookmark_id FROM bookmarks 
            WHERE user_id = %s AND verse_id = %s
        """, (user['user_id'], verse_id))
        existing = cursor.fetchone()
        
        if existing:
            return jsonify(status='error', message='Verse already bookmarked'), 400
        
        # Add new bookmark
        cursor.execute("""
            INSERT INTO bookmarks (user_id, verse_id, bookmark_note)
            VALUES (%s, %s, %s)
        """, (user['user_id'], verse_id, note))
        conn.commit()
        
        return jsonify(status='success', message='Bookmark added successfully')
    except Exception as e:
        print(f"Error adding bookmark: {e}")
        return jsonify(status='error', message='Failed to add bookmark'), 500
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/delete-bookmark/<int:bookmark_id>', methods=['POST'])
def delete_bookmark(bookmark_id):
    if 'username' not in session:
        return jsonify(status='error', message='Not logged in'), 401
    
    user = get_user_by_username(session['username'])
    if not user:
        return jsonify(status='error', message='User not found'), 404
    
    conn = get_db_connection()
    if not conn:
        return jsonify(status='error', message='Database error'), 500
    
    cursor = conn.cursor()
    try:
        # Verify the bookmark belongs to the user
        cursor.execute("""
            SELECT bookmark_id FROM bookmarks 
            WHERE bookmark_id = %s AND user_id = %s
        """, (bookmark_id, user['user_id']))
        if not cursor.fetchone():
            return jsonify(status='error', message='Bookmark not found'), 404
        
        # Delete the bookmark
        cursor.execute("""
            DELETE FROM bookmarks 
            WHERE bookmark_id = %s AND user_id = %s
        """, (bookmark_id, user['user_id']))
        conn.commit()
        
        return jsonify(status='success', message='Bookmark deleted successfully')
    except Exception as e:
        print(f"Error deleting bookmark: {e}")
        return jsonify(status='error', message='Failed to delete bookmark'), 500
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/get-note/<int:verse_id>', methods=['GET'])
def get_note(verse_id):
    if 'username' not in session:
        print("User not logged in")
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    conn = None
    cursor = None
    try:
        print(f"Getting note for verse_id: {verse_id}, username: {session['username']}")
        
        conn = get_db_connection()
        if not conn:
            print("Database connection failed")
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Get user_id from username
        print(f"Getting user_id for username: {session['username']}")
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()
        if not user:
            print("User not found")
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        print(f"Found user_id: {user['user_id']}")
        
        # Get existing note for this verse
        print(f"Getting note for user_id: {user['user_id']}, verse_id: {verse_id}")
        cursor.execute("""
            SELECT note_id, note_text 
            FROM additional_notes 
            WHERE user_id = %s AND verse_id = %s
        """, (user['user_id'], verse_id))
        
        note = cursor.fetchone()
        print(f"Note found: {note}")
        
        if note:
            return jsonify({'status': 'success', 'note': note})
        else:
            return jsonify({'status': 'success', 'note': None})
            
    except Exception as e:
        print(f"Error getting note: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'status': 'error', 'message': f'Failed to get note: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@views_bp.route('/add-note', methods=['POST'])
def add_note():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    conn = None
    cursor = None
    try:
        data = request.get_json()
        verse_id = data.get('verse_id')
        surah_id = data.get('surah_id')
        note_id = data.get('note_id')
        note_text = data.get('note_text')

        if not all([verse_id, note_text]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        cursor = conn.cursor()

        # Get user_id from username
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        user_id = user[0]  # Access the first element of the tuple

        if note_id:
            # Update existing note
            cursor.execute("""
                UPDATE additional_notes 
                SET note_text = %s, updated_at = CURRENT_TIMESTAMP
                WHERE note_id = %s AND user_id = %s
            """, (note_text, note_id, user_id))
        else:
            # Insert new note
            cursor.execute("""
                INSERT INTO additional_notes (user_id, verse_id, note_text)
                VALUES (%s, %s, %s)
            """, (user_id, verse_id, note_text))

        conn.commit()
        return jsonify({'status': 'success', 'message': 'Note saved successfully'})

    except Exception as e:
        print(f"Error saving note: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to save note: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@views_bp.route('/notes')
def notes():
    if 'username' not in session:
        return redirect(url_for('views.login'))
    
    user = get_user_by_username(session['username'])
    if not user:
        return redirect(url_for('views.login'))
    
    conn = get_db_connection()
    if not conn:
        return render_template('pages/notes.html', notes=[])
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all notes for the user with surah information
        cursor.execute("""
            SELECT an.*, s.name as surah_name, s.number as surah_number
            FROM additional_notes an
            JOIN surahs s ON SUBSTRING_INDEX(an.verse_id, ':', 1) = s.number
            WHERE an.user_id = %s
            ORDER BY an.created_at DESC
        """, (user['user_id'],))
        notes = cursor.fetchall()
        
        # Enrich notes with ayah number
        for note in notes:
            note['ayah_number'] = note['verse_id'].split(':')[1]
        
        return render_template('pages/notes.html', notes=notes)
    except Exception as e:
        print(f"Error fetching notes: {e}")
        return render_template('pages/notes.html', notes=[])
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/delete-note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'username' not in session:
        return jsonify(status='error', message='Not logged in'), 401
    
    user = get_user_by_username(session['username'])
    if not user:
        return jsonify(status='error', message='User not found'), 404
    
    conn = get_db_connection()
    if not conn:
        return jsonify(status='error', message='Database connection failed'), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM additional_notes 
            WHERE note_id = %s AND user_id = %s
        """, (note_id, user['user_id']))
        conn.commit()
        return jsonify(status='success')
    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify(status='error', message='Failed to delete note'), 500
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/get-ayah-of-the-day')
def get_ayah_of_the_day():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401
    
    try:
        # Get the current date as a seed for consistent daily ayah
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Getting ayah for date: {today}")
        
        # Use the date as a seed to get a consistent random number
        import hashlib
        seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
        print(f"Generated seed: {seed}")
        
        # Get total number of surahs
        surahs = current_app.config['SURAH_LIST']
        total_surahs = len(surahs)
        print(f"Total surahs: {total_surahs}")
        
        # Generate a random surah number (1-based)
        random_surah = (seed % total_surahs) + 1
        print(f"Selected surah: {random_surah}")
        
        # Get the surah metadata
        surah_meta = get_surah_metadata(surahs, random_surah)
        if not surah_meta:
            print(f"Invalid surah metadata for surah {random_surah}")
            return jsonify({'status': 'error', 'message': 'Invalid surah'}), 400
        
        # Get total number of ayahs in the surah
        total_ayahs = surah_meta.get('ayah_count', 0)
        if total_ayahs == 0:
            print(f"Invalid ayah count for surah {random_surah}")
            return jsonify({'status': 'error', 'message': 'Invalid ayah count'}), 400
        
        # Generate a random ayah number (1-based)
        random_ayah = (seed % total_ayahs) + 1
        print(f"Selected ayah: {random_ayah}")
        
        # Get the English translation from pre-loaded texts
        # The structure is: {'english': {'quran': {'en.sahih': {'quran': {'en.sahih': {...}}}}}}
        english_text = current_app.config['QURAN_TEXTS']['english']['quran']['en.sahih']['quran']['en.sahih']
        
        # Find the ayah in the English translation
        ayah_text = None
        for ayah_id, ayah_data in english_text.items():
            if ayah_data.get('surah') == random_surah and ayah_data.get('ayah') == random_ayah:
                ayah_text = ayah_data.get('verse', '')
                break
        
        if not ayah_text:
            print(f"No translation found for surah {random_surah}, ayah {random_ayah}")
            return jsonify({'status': 'error', 'message': 'Translation not found'}), 404
        
        print(f"Found ayah text: {ayah_text[:50]}...")
        
        return jsonify({
            'status': 'success',
            'ayah': {
                'surah_number': random_surah,
                'surah_name': surah_meta.get('name'),
                'surah_name_arabic': surah_meta.get('arabic_name'),
                'ayah_number': random_ayah,
                'text': ayah_text
            }
        })
        
    except Exception as e:
        print(f"Error getting ayah of the day: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500
