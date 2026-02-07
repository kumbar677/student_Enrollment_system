from app import create_app
from models import db, CourseVideo
import sqlalchemy

app = create_app()

def upgrade():
    with app.app_context():
        inspector = sqlalchemy.inspect(db.engine)
        if 'course_videos' not in inspector.get_table_names():
            print("Creating course_videos table...")
            CourseVideo.__table__.create(db.engine)
            print("Table created successfully.")
        else:
            print("Table course_videos already exists.")

if __name__ == "__main__":
    upgrade()
