from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Check if column exists is hard in generic SQL, so we rely on 'try'
            try:
                conn.execute(text("ALTER TABLE courses ADD COLUMN fee FLOAT DEFAULT 500.0"))
                conn.commit()
                print("Successfully added 'fee' column to 'courses' table.")
            except Exception as e:
                print(f"Column might already exist or error: {e}")
                
            # Allow NULLs initially or set defaults, but here we set default 500.0
            
    except Exception as e:
        print(f"Error connecting or executing: {e}")
