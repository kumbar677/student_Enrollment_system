
import mysql.connector

def kill_processes():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2003',
            database='enrollment_db'
        )
        cursor = conn.cursor()
        cursor.execute("SHOW PROCESSLIST")
        processes = cursor.fetchall()
        
        my_id = conn.connection_id
        
        for p in processes:
            pid = p[0]
            user = p[1]
            db = p[3]
            command = p[4]
            state = p[6]
            info = p[7]
            
            if pid != my_id and user == 'root': # Be careful
                print(f"Killing process {pid} ({command}, {state}, {info})")
                try:
                    cursor.execute(f"KILL {pid}")
                except Exception as kille:
                    print(f"Failed to kill {pid}: {kille}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    kill_processes()
