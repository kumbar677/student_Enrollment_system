
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfgen import canvas
import os

def draw_box(c, x, y, title, attributes, width=150, line_height=14):
    # Calculate height based on attributes
    header_height = 20
    body_height = len(attributes) * line_height + 10
    total_height = header_height + body_height
    
    # Draw Header (Entity Name)
    c.setFillColor(colors.lightgrey)
    c.setStrokeColor(colors.black)
    c.rect(x, y - header_height, width, header_height, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x + width/2, y - header_height + 6, title)
    
    # Draw Body (Attributes)
    c.setFillColor(colors.white)
    c.rect(x, y - total_height, width, body_height, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    
    text_y = y - header_height - 12
    for attr in attributes:
        # Check if key (PK/FK) to bold or mark
        display_text = attr
        if "(PK)" in attr or "id" == attr:
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 10)
            
        c.drawString(x + 5, text_y, display_text)
        text_y -= line_height
        
    return (x + width/2, y - total_height/2, width, total_height) # Return center point and size for connections

def connect_boxes(c, box1, box2, label=""):
    # box format: (center_x, center_y, width, height)
    x1, y1 = box1[0], box1[1]
    x2, y2 = box2[0], box2[1]
    
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    
    # Simple direct line for now (center to center) - could be improved to edge-to-edge
    c.line(x1, y1, x2, y2)
    
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # White background for label
        label_width = c.stringWidth(label, "Helvetica", 9) + 6
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.white) 
        c.rect(mid_x - label_width/2, mid_y - 5, label_width, 10, fill=1, stroke=1)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawCentredString(mid_x, mid_y - 3, label)

def create_er_diagram_box():
    pdf_file = "ER_Diagram_Box.pdf"
    c = canvas.Canvas(pdf_file, pagesize=landscape(A3))
    width, height = landscape(A3)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 50, "ER Diagram (Schema Structure)")
    
    # --- DATA DEFINITIONS ---
    users_attrs = ["id (PK)", "name", "email", "password_hash", "role", "created_at"]
    student_attrs = ["id (PK)", "user_id (FK)", "enrollment_no", "phone", "address", "dob", "profile_image"]
    course_attrs = ["id (PK)", "course_code", "name", "credits", "seats", "fee", "category", "level", "stream", "description", "link"]
    enroll_attrs = ["id (PK)", "student_id (FK)", "course_id (FK)", "status", "date_enrolled", "transaction_ref", "receipt_img"]
    
    section_attrs = ["id (PK)", "course_id (FK)", "title", "section_order"]
    video_attrs = ["id (PK)", "course_id (FK)", "section_id (FK)", "title", "video_url", "duration", "sequence"]

    # --- DRAWING BOXES ---
    # Layout strategy: 
    # Users (Left) -> StudentDetails (Center-Left) -> Enrollment (Center-Right)
    #                                                    |
    #                                                 Course (Right)
    #                                                    |
    #                                              Sections -> Videos
    
    # Coordinates (Approximate for A3 Landscape)
    # Top Row
    user_box = draw_box(c, 50, 600, "Users", users_attrs)
    
    stud_box = draw_box(c, 300, 600, "StudentDetails", student_attrs)
    
    enroll_box = draw_box(c, 550, 600, "Enrollments", enroll_attrs)
    
    # Bottom Row / Right Side
    course_box = draw_box(c, 550, 400, "Courses", course_attrs)
    
    section_box = draw_box(c, 800, 400, "CourseSections", section_attrs)
    
    video_box = draw_box(c, 800, 200, "CourseVideos", video_attrs)

    # --- CONNECTIONS ---
    connect_boxes(c, user_box, stud_box, "1..1")
    connect_boxes(c, stud_box, enroll_box, "1..N")
    
    connect_boxes(c, course_box, enroll_box, "1..N")
    
    connect_boxes(c, course_box, section_box, "1..N")
    connect_boxes(c, course_box, video_box, "1..N")
    connect_boxes(c, section_box, video_box, "1..N")

    c.save()
    print(f"ER Diagram PDF generated: {os.path.abspath(pdf_file)}")

if __name__ == "__main__":
    create_er_diagram_box()
