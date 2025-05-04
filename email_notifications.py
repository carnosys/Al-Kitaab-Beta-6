from flask import Flask
from flask_mail import Mail, Message
from datetime import datetime, time, timedelta
import threading
import time as time_module
from services import fetch_all

# Initialize Flask-Mail
mail = Mail()

def send_notification_email(app, user_email, username):
    """Send a notification email to the user."""
    try:
        with app.app_context():
            msg = Message(
                subject="Time to Read Quran",
                recipients=[user_email],
                body=f"Dear {username},\n\nIt's time to read the Quran according to your preferred reading window. Please take some time to read and reflect.\n\nBest regards,\nAl-Kitab Team"
            )
            mail.send(msg)
            print(f"Email sent successfully to {user_email}")
            return True
    except Exception as e:
        print(f"Error sending email to {user_email}: {e}")
        return False

def convert_to_time(time_value):
    """Convert a time value from the database to a time object."""
    if isinstance(time_value, timedelta):
        # Convert timedelta to time
        total_seconds = int(time_value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return time(hour=hours, minute=minutes)
    elif isinstance(time_value, str):
        # Convert string to time
        time_obj = datetime.strptime(time_value, '%H:%M:%S').time()
        return time(hour=time_obj.hour, minute=time_obj.minute)
    elif isinstance(time_value, time):
        return time(hour=time_value.hour, minute=time_value.minute)
    return time_value

def check_and_send_notifications(app):
    """Check for users whose reading window has started and send notifications."""
    while True:
        current_time = datetime.now().time()
        # Create a time object with only hours and minutes
        current_time_minutes = time(hour=current_time.hour, minute=current_time.minute)
        
        # Get all users with notification enabled
        users = fetch_all("""
            SELECT u.user_id, u.user_email, u.username, ug.window_start, ug.window_end 
            FROM users u
            JOIN user_goals ug ON u.user_id = ug.user_id
            WHERE u.notification_enabled = 1
            AND ug.window_start IS NOT NULL
            AND ug.window_end IS NOT NULL
        """)
        
        for user in users:
            window_start = convert_to_time(user['window_start'])
            
            # Check if current time exactly matches window start time (ignoring seconds)
            if current_time_minutes == window_start:
                print(f"Window start time matched for user {user['username']}: {window_start}")
                send_notification_email(app, user['user_email'], user['username'])
        
        # Sleep for 1 minute before checking again
        time_module.sleep(60)

def start_notification_service(app):
    """Start the notification service in a background thread."""
    thread = threading.Thread(target=check_and_send_notifications, args=(app,))
    thread.daemon = True
    thread.start() 