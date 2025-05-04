import unittest
from unittest.mock import patch, MagicMock, call
from services import update_user_streaks

class TestUpdateUserStreaks(unittest.TestCase):
    def setUp(self):
        # Common mock setup for all tests
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_get_db_connection = patch('services.get_db_connection').start()
        self.mock_get_db_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

    def tearDown(self):
        patch.stopall()

    def test_streak_increments_when_goal_met(self):
        # Mock data for user goals and streaks
        self.mock_cursor.fetchall.return_value = [
                {
                    'user_id': 1,
                    'verses_per_session': 10,
                    'window_start': 8,  # 8 AM
                    'window_end': 20,  # 8 PM
                    'current_streak': 2,
                    'longest_streak': 5
                }
        ]
        
        # Mock the verses count result
        self.mock_cursor.fetchone.return_value = {'total_verses': 12}  # User read 12 verses, meeting the goal

        # Call the function
        result = update_user_streaks()

        # Assertions
        self.assertTrue(result)
        
        # Verify the SQL queries were called with correct parameters
        expected_calls = [
            call("""
            SELECT ug.user_id, ug.verses_per_session, ug.window_start, ug.window_end,
                   us.current_streak, us.longest_streak
            FROM user_goals ug
            JOIN user_streaks us ON ug.user_id = us.user_id
            WHERE ug.recurring = 1 AND ug.completed = 0
            """),
            call("""
            SELECT COALESCE(SUM(verses_read), 0) AS total_verses
            FROM reading_sessions
            WHERE user_id = %s
            AND completed = 1
            AND start_time >= CURDATE() + INTERVAL %s HOUR
            AND start_time <= CURDATE() + INTERVAL %s HOUR
            """, (1, 8, 20)),
            call("""
            UPDATE user_streaks
            SET current_streak = %s, longest_streak = %s, last_read_date = CURDATE()
            WHERE user_id = %s
            """, (3, 5, 1))
        ]
        
        # Verify all expected calls were made
        self.mock_cursor.execute.assert_has_calls(expected_calls, any_order=False)

    def test_streak_resets_when_goal_not_met(self):
        # Mock data for user goals and streaks
        self.mock_cursor.fetchall.return_value = [
            {
                'user_id': 1,
                'verses_per_session': 10,
                'window_start': 8,
                'window_end': 20,
                'current_streak': 3,
                'longest_streak': 5
            }
        ]
        
        # Mock the verses count result - user only read 5 verses
        self.mock_cursor.fetchone.return_value = {'total_verses': 5}

        # Call the function
        result = update_user_streaks()

        # Assertions
        self.assertTrue(result)
        
        # Verify the streak was reset
        self.mock_cursor.execute.assert_any_call("""
            UPDATE user_streaks
            SET current_streak = 0, last_read_date = CURDATE()
            WHERE user_id = %s
            """, (1,))

    def test_no_reading_sessions(self):
        # Mock data for user goals and streaks
        self.mock_cursor.fetchall.return_value = [
            {
                'user_id': 1,
                'verses_per_session': 10,
                'window_start': 8,
                'window_end': 20,
                'current_streak': 2,
                'longest_streak': 5
            }
        ]
        
        # Mock the verses count result - no verses read
        self.mock_cursor.fetchone.return_value = {'total_verses': 0}

        # Call the function
        result = update_user_streaks()

        # Assertions
        self.assertTrue(result)
        
        # Verify the streak was reset
        self.mock_cursor.execute.assert_any_call("""
            UPDATE user_streaks
            SET current_streak = 0, last_read_date = CURDATE()
            WHERE user_id = %s
            """, (1,))

    def test_longest_streak_updated(self):
        # Mock data for user goals and streaks
        self.mock_cursor.fetchall.return_value = [
            {
                'user_id': 1,
                'verses_per_session': 10,
                'window_start': 8,
                'window_end': 20,
                'current_streak': 4,
                'longest_streak': 4
            }
        ]
        
        # Mock the verses count result - user read enough verses
        self.mock_cursor.fetchone.return_value = {'total_verses': 12}

        # Call the function
        result = update_user_streaks()

        # Assertions
        self.assertTrue(result)
        
        # Verify both current and longest streak were updated
        self.mock_cursor.execute.assert_any_call("""
            UPDATE user_streaks
            SET current_streak = %s, longest_streak = %s, last_read_date = CURDATE()
            WHERE user_id = %s
            """, (5, 5, 1))

    def test_multiple_users(self):
        # Mock data for multiple users
        self.mock_cursor.fetchall.return_value = [
            {
                'user_id': 1,
                'verses_per_session': 10,
                'window_start': 8,
                'window_end': 20,
                'current_streak': 2,
                'longest_streak': 5
            },
            {
                'user_id': 2,
                'verses_per_session': 15,
                'window_start': 9,
                'window_end': 21,
                'current_streak': 1,
                'longest_streak': 3
            }
        ]
        
        # Mock the verses count results for each user
        self.mock_cursor.fetchone.side_effect = [
            {'total_verses': 12},  # User 1 read 12 verses (meets goal)
            {'total_verses': 10}   # User 2 didn't meet goal (15 required)
        ]

        # Call the function
        result = update_user_streaks()

        # Assertions
        self.assertTrue(result)
        
        # Expected SQL calls
        expected_calls = [
            # Initial query to get all users' goals
            call("""
            SELECT ug.user_id, ug.verses_per_session, ug.window_start, ug.window_end,
                   us.current_streak, us.longest_streak
            FROM user_goals ug
            JOIN user_streaks us ON ug.user_id = us.user_id
            WHERE ug.recurring = 1 AND ug.completed = 0
            """),
            # User 1 verses query
            call("""
            SELECT COALESCE(SUM(verses_read), 0) AS total_verses
            FROM reading_sessions
            WHERE user_id = %s
            AND completed = 1
            AND start_time >= CURDATE() + INTERVAL %s HOUR
            AND start_time <= CURDATE() + INTERVAL %s HOUR
            """, (1, 8, 20)),
            # User 1 streak update (increment)
            call("""
            UPDATE user_streaks
            SET current_streak = %s, longest_streak = %s, last_read_date = CURDATE()
            WHERE user_id = %s
            """, (3, 5, 1)),
            # User 2 verses query
            call("""
            SELECT COALESCE(SUM(verses_read), 0) AS total_verses
            FROM reading_sessions
            WHERE user_id = %s
            AND completed = 1
            AND start_time >= CURDATE() + INTERVAL %s HOUR
            AND start_time <= CURDATE() + INTERVAL %s HOUR
            """, (2, 9, 21)),
            # User 2 streak update (reset)
            call("""
            UPDATE user_streaks
            SET current_streak = 0, last_read_date = CURDATE()
            WHERE user_id = %s
            """, (2,))
        ]
        
        # Verify all expected calls were made in the correct order
        self.mock_cursor.execute.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(self.mock_cursor.execute.call_count, 5)  # 1 initial query + 2 queries per user

if __name__ == '__main__':
    unittest.main()
