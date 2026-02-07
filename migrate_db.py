from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists to avoid error
        with db.engine.connect() as conn:
            # Simple check or just try-except
            try:
                conn.execute(text("ALTER TABLE enrollments ADD COLUMN transaction_reference VARCHAR(100)"))
                conn.execute(text("ALTER TABLE enrollments ADD COLUMN receipt_image VARCHAR(255)"))
                conn.commit()
                print("Successfully added columns to 'enrollments' table.")
            except Exception as e:
                print(f"Columns might already exist or error: {e}")
    except Exception as e:
        print(f"Error connecting or executing: {e}")
