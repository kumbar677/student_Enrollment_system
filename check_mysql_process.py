
import mysql.connector

def check_processes():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2003',
            database='enrollment_db'
        )
        cursor = conn.cursor()
        cursor.execute("SHOW PROCESSLIST")
        for row in cursor.fetchall():
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    check_processes()
