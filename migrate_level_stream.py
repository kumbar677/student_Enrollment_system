
import mysql.connector

def migrate():
    print("Migrating database to include Level and Stream columns in Courses table...")
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2003',
            database='enrollment_db'
        )
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("DESCRIBE courses")
        columns = [row[0] for row in cursor.fetchall()]
        
        if 'level' not in columns:
            print("Adding 'level' column...")
            cursor.execute("ALTER TABLE courses ADD COLUMN level VARCHAR(50) DEFAULT '1st PU'")
        else:
            print("'level' column already exists.")
            
        if 'stream' not in columns:
            print("Adding 'stream' column...")
            cursor.execute("ALTER TABLE courses ADD COLUMN stream VARCHAR(50) DEFAULT 'Science'")
        else:
            print("'stream' column already exists.")
            
        conn.commit()
        print("Migration successful!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    migrate()
