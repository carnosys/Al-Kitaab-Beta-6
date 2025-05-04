# services.py
from db import get_db_connection

def fetch_one(query, params):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def fetch_all(query, params=()):
    """Fetch all rows from a query."""
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def execute(query, params):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()
    return True

# user operations

def get_user_by_username(username):
    return fetch_one("SELECT * FROM users WHERE username = %s", (username,))

def get_user_by_email(email):
    return fetch_one("SELECT * FROM users WHERE user_email = %s", (email,))

def get_user_by_username_or_email(username, email):
    return fetch_one(
        "SELECT * FROM users WHERE username = %s OR user_email = %s",
        (username, email)
    )

def create_user(username, email, password):
    return execute(
        "INSERT INTO users (username, user_email, password, is_first_login, role) "
        "VALUES (%s, %s, %s, TRUE, 'user')",
        (username, email, password)
    )

def update_last_seen(username, surah_id, ayah_id):
    return execute(
        "UPDATE users SET last_seen_surah = %s, last_seen_ayah = %s WHERE username = %s",
        (surah_id, ayah_id, username)
    )

def get_last_seen(username):
    return fetch_one(
        "SELECT last_seen_surah, last_seen_ayah FROM users WHERE username = %s",
        (username,)
    )

def update_user_basic_info(user_id, gender, country, script, language):
    return execute(
        "UPDATE users SET gender=%s, country=%s, preferred_script=%s, preffered_languge=%s, is_first_login=FALSE "
        "WHERE user_id=%s",
        (gender, country, script, language, user_id)
    )

def insert_user_goals(user_id, verses, window_start, window_end, freq, interval):
    return execute(
        "INSERT INTO user_goals (user_id, goal_type, target_type, target_value, start_date, recurring, "
        "verses_per_session, window_start, window_end, reminder_freq, reminder_interval_minutes) "
        "VALUES (%s, 'reading', 'verses', %s, CURDATE(), 1, %s, %s, %s, %s, %s)",
        (user_id, verses, verses, window_start, window_end, freq, interval)
    )

def init_user_streak(user_id):
    return execute(
        "INSERT INTO user_streaks (user_id, current_streak, longest_streak, last_read_date, streak_protected_until, freeze_count) "
        "VALUES (%s, 0, 0, NULL, NULL, 0)",
        (user_id,)
    )

def start_reading_session(user_id, start_ayah):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reading_sessions (user_id, start_time, verses_read, completed) "
            "VALUES (%s, NOW(), 0, 0)",
            (user_id,)
        )
        session_id = cursor.lastrowid
        conn.commit()
        return session_id
    except Exception as e:
        print(f"Error starting session: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def end_reading_session(session_id, end_ayah, verses_read, duration):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        # Update the reading session
        cursor.execute(
            "UPDATE reading_sessions SET end_time = NOW(), verses_read = %s, "
            "duration_seconds = %s, completed = 1 WHERE reading_id = %s",
            (verses_read, duration, session_id)
        )
        
        # Update user streak
        cursor.execute(
            "UPDATE user_streaks SET last_read_date = CURDATE() "
            "WHERE user_id = (SELECT user_id FROM reading_sessions WHERE reading_id = %s)",
            (session_id,)
        )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error ending session: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_streaks():
    """
    Update user streaks based on their goals and reading sessions.
    This function should be called when the `window_end` time is reached.
    """
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch all active user goals
        cursor.execute("""
            SELECT ug.user_id, ug.verses_per_session, ug.window_start, ug.window_end,
                   us.current_streak, us.longest_streak
            FROM user_goals ug
            JOIN user_streaks us ON ug.user_id = us.user_id
            WHERE ug.recurring = 1 AND ug.completed = 0
            """)
        user_goals = cursor.fetchall()

        for goal in user_goals:
            user_id = int(goal['user_id'])
            verses_per_session = int(goal['verses_per_session'])
            window_start = goal['window_start']
            window_end = goal['window_end']
            current_streak = int(goal['current_streak'])
            longest_streak = int(goal['longest_streak'])

            # Convert window times to strings if they're time objects
            window_start_str = window_start.strftime('%H:%M:%S') if hasattr(window_start, 'strftime') else str(window_start)
            window_end_str = window_end.strftime('%H:%M:%S') if hasattr(window_end, 'strftime') else str(window_end)

            # Calculate total verses read within the time window
            cursor.execute("""
            SELECT COALESCE(SUM(verses_read), 0) AS total_verses
            FROM reading_sessions
            WHERE user_id = %s
            AND completed = 1
            AND TIME(start_time) >= %s
            AND TIME(start_time) <= %s
            AND DATE(start_time) = CURDATE()
            """, (user_id, window_start_str, window_end_str))
            
            result = cursor.fetchone()
            total_verses = int(result['total_verses'])

            # Update streak based on goal achievement
            if total_verses >= verses_per_session:
                # Increment streak
                new_streak = current_streak + 1
                longest_streak = max(longest_streak, new_streak)
                cursor.execute("""
                UPDATE user_streaks
                SET current_streak = %s, longest_streak = %s, last_read_date = CURDATE()
                WHERE user_id = %s
                """, (new_streak, longest_streak, user_id))
            else:
                # Reset streak
                cursor.execute("""
                UPDATE user_streaks
                SET current_streak = 0, last_read_date = CURDATE()
                WHERE user_id = %s
                """, (user_id,))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating streaks: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()