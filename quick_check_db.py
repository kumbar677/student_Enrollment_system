
import mysql.connector

def check():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2003',
            database='enrollment_db'
        )
        cursor = conn.cursor()
        cursor.execute("DESCRIBE courses")
        columns = [row[0] for row in cursor.fetchall()]
        print("Columns in 'courses' table:", columns)
        
        has_level = 'level' in columns
        has_stream = 'stream' in columns
        
        print(f"Has 'level': {has_level}")
        print(f"Has 'stream': {has_stream}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    check()
