from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Add reset_otp column
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_otp VARCHAR(6)"))
            print("Added reset_otp column.")
    except Exception as e:
        print(f"reset_otp column might already exist: {e}")

    # Add reset_otp_expiry column
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_otp_expiry DATETIME"))
            print("Added reset_otp_expiry column.")
    except Exception as e:
        print(f"reset_otp_expiry column might already exist: {e}")
        
    print("Database update complete.")
