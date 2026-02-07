from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Inspection for MySQL/SQLite
            result = conn.execute(text("SELECT * FROM courses LIMIT 1;"))
            print(f"Columns: {result.keys()}")
    except Exception as e:
        print(f"Error: {e}")
