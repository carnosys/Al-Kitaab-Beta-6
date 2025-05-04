import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='al_kitab_user',
        password='yourpassword',
        database='Al_Kitab'
    )
    print("Successfully connected!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")