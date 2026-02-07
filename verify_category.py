from app import create_app
from models import Course

app = create_app()

with app.app_context():
    try:
        course = Course.query.first()
        if course:
            print(f"Course: {course.name}, Category: {course.category}")
        else:
            print("No courses found.")
    except Exception as e:
        print(f"Error accessing category: {e}")
