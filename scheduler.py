from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
from services import update_user_streaks, get_db_connection

def check_and_update_streaks():
    """Check and update streaks for users whose window has ended."""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all unique window_end times
        cursor.execute("""
            SELECT DISTINCT window_end 
            FROM user_goals 
            WHERE recurring = 1 AND completed = 0
        """)
        window_ends = cursor.fetchall()
        
        current_time = datetime.now().time()
        
        # Check if current time matches any window_end time
        for window in window_ends:
            window_end = window['window_end']
            if isinstance(window_end, time):
                # Compare time objects directly
                if current_time.hour == window_end.hour and current_time.minute == window_end.minute:
                    print(f"Running streak update for window end time: {window_end}")
                    update_user_streaks()
            else:
                # Handle case where window_end is stored as string (HH:MM:SS)
                try:
                    window_time = datetime.strptime(str(window_end), '%H:%M:%S').time()
                    if current_time.hour == window_time.hour and current_time.minute == window_time.minute:
                        print(f"Running streak update for window end time: {window_end}")
                        update_user_streaks()
                except ValueError:
                    print(f"Invalid time format for window_end: {window_end}")
                
    except Exception as e:
        print(f"Error in check_and_update_streaks: {e}")
    finally:
        cursor.close()
        conn.close()

def start_streak_scheduler():
    """Start the background scheduler for streak updates."""
    scheduler = BackgroundScheduler()
    
    # Run every minute to check for window_end times
    scheduler.add_job(
        check_and_update_streaks,
        CronTrigger(minute='*'),  # Run every minute
        id='streak_update_job',
        replace_existing=True
    )
    
    scheduler.start()
    print("Streak update scheduler started") 