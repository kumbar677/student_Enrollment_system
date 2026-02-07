from app import create_app
from models import db
from sqlalchemy import text
import sqlalchemy

app = create_app()

with app.app_context():
    print("Attempting to add 'category' column to 'courses' table...")
    try:
        with db.engine.connect() as conn:
            # Check if column exists first to avoid error if run multiple times
            try:
                # Try simple select
                conn.execute(text("SELECT category FROM courses LIMIT 1"))
                print("'category' column already exists.")
            except sqlalchemy.exc.OperationalError:
                # Column likely missing
                print("Column missing, adding it now...")
                conn.execute(text("ALTER TABLE courses ADD COLUMN category VARCHAR(50) DEFAULT 'General' NOT NULL"))
                conn.commit()
                print("Successfully added 'category' column.")
            except sqlalchemy.exc.ProgrammingError:
                 # Column likely missing (mysql specific error sometimes)
                print("Column missing (ProgrammingError), adding it now...")
                conn.execute(text("ALTER TABLE courses ADD COLUMN category VARCHAR(50) DEFAULT 'General' NOT NULL"))
                conn.commit()
                print("Successfully added 'category' column.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
