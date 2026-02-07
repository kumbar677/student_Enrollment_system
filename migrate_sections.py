from app import create_app
from models import db, CourseSection, CourseVideo
import sqlalchemy
from sqlalchemy import text

app = create_app()

def upgrade():
    with app.app_context():
        inspector = sqlalchemy.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # 1. Create course_sections if not exists
        if 'course_sections' not in tables:
            print("Creating course_sections table...")
            CourseSection.__table__.create(db.engine)
        
        # 2. Check course_videos for new columns
        columns = [c['name'] for c in inspector.get_columns('course_videos')]
        
        if 'section_id' not in columns:
            print("Adding section_id to course_videos...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE course_videos ADD COLUMN section_id INT"))
                conn.execute(text("ALTER TABLE course_videos ADD CONSTRAINT fk_course_videos_section FOREIGN KEY (section_id) REFERENCES course_sections(id) ON DELETE CASCADE"))
        
        if 'duration' not in columns:
            print("Adding duration to course_videos...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE course_videos ADD COLUMN duration VARCHAR(20)"))
                
        print("Database schema updated successfully.")

if __name__ == "__main__":
    upgrade()
