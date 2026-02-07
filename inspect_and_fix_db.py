from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('courses')
    print("Columns in 'courses' table:")
    found_fee = False
    for col in columns:
        print(f"- {col['name']} ({col['type']})")
        if col['name'] == 'fee':
            found_fee = True
            
    if not found_fee:
        print("\nMISSING 'fee' COLUMN! specific migration needed.")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE courses ADD COLUMN fee FLOAT DEFAULT 500.0"))
                conn.commit()
            print("Successfully patched 'fee' column.")
        except Exception as e:
            print(f"Error patching: {e}")
    else:
        print("\n'fee' column is present.")
