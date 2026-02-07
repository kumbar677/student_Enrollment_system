from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(courses);")).fetchall()
            columns = [row[1] for row in result]
            
            if 'category' not in columns:
                print("Adding 'category' column to 'courses' table...")
                conn.execute(text("ALTER TABLE courses ADD COLUMN category VARCHAR(50) DEFAULT 'General' NOT NULL"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("'category' column already exists.")
    except Exception as e:
        print(f"Error: {e}")
