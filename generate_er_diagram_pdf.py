from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfgen import canvas
import math
import os

def draw_entity(c, x, y, name, width=120, height=60):
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.lightblue)
    c.rect(x - width/2, y - height/2, width, height, fill=1)
    c.setFillColor(colors.black)
    c.drawCentredString(x, y - 5, name)
    return (x, y)

def draw_attribute(c, x, y, name, width=80, height=40, key=False):
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    p = c.beginPath()
    p.ellipse(x - width/2, y - height/2, width, height)
    c.drawPath(p, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    if key:
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x, y - 4, f"_{name}_") 
    else:
        c.setFont("Helvetica", 10)
        c.drawCentredString(x, y - 4, name)
    return (x, y)

def draw_relationship(c, x, y, name, width=100, height=60):
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.lightgrey)
    p = c.beginPath()
    p.moveTo(x, y + height/2)
    p.lineTo(x + width/2, y)
    p.lineTo(x, y - height/2)
    p.lineTo(x - width/2, y)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.drawCentredString(x, y - 4, name)
    return (x, y)

def connect(c, p1, p2, label=""):
    c.setStrokeColor(colors.black)
    c.line(p1[0], p1[1], p2[0], p2[1])
    if label:
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 8)
        c.drawString(mid_x + 5, mid_y + 5, label)

def create_er_diagram():
    pdf_file = "ER_Diagram.pdf"
    c = canvas.Canvas(pdf_file, pagesize=landscape(A3))
    width, height = landscape(A3)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 50, "Entity Relationship Diagram - Student Enrollment System")
    
    c.setFont("Helvetica", 10)

    # --- ENTITIES ---
    user_pos = draw_entity(c, 200, 400, "User")
    student_pos = draw_entity(c, 500, 400, "StudentDetails")
    enroll_pos = draw_entity(c, 800, 400, "Enrollment")
    course_pos = draw_entity(c, 800, 150, "Course")
    
    # NEW: Admin Entity (Conceptual)
    admin_pos = draw_entity(c, 500, 550, "Admin")

    # --- RELATIONSHIPS ---
    # User - StudentDetails
    rel_has_pos = draw_relationship(c, 350, 400, "Has")
    connect(c, user_pos, rel_has_pos, "1")
    connect(c, rel_has_pos, student_pos, "1")

    # StudentDetails - Enrollment
    rel_enrolls_pos = draw_relationship(c, 650, 400, "Makes")
    connect(c, student_pos, rel_enrolls_pos, "1")
    connect(c, rel_enrolls_pos, enroll_pos, "N")

    # Course - Enrollment
    rel_course_enr_pos = draw_relationship(c, 800, 275, "For")
    connect(c, course_pos, rel_course_enr_pos, "1")
    connect(c, rel_course_enr_pos, enroll_pos, "N")
    
    # NEW: Admin Relationships
    # Admin - StudentDetails (Manages)
    rel_manages_stu_pos = draw_relationship(c, 500, 475, "Manages")
    connect(c, admin_pos, rel_manages_stu_pos, "1")
    connect(c, rel_manages_stu_pos, student_pos, "N")
    
    # Admin - Course (Manages/Creates)
    # Drawing a long line connection
    rel_manages_course_pos = draw_relationship(c, 200, 150, "Manages")
    # Connect Admin to this relationship (long visual line)
    connect(c, admin_pos, rel_manages_course_pos, "1")
    connect(c, rel_manages_course_pos, course_pos, "N")

    # --- ATTRIBUTES ---
    
    # Admin Attributes (Conceptual - inherited from User but showing explicit role)
    at_admin = [
        ("id", 420, 600, True), ("name", 500, 600, False), ("email", 580, 600, False)
    ]
    for name, x, y, key in at_admin:
        pos = draw_attribute(c, x, y, name, key=key)
        connect(c, admin_pos, pos)

    # --- ATTRIBUTES ---
    
    # User Attributes
    at_users = [
        ("id", 100, 460, True), ("name", 100, 410, False), 
        ("email", 100, 360, False), ("role", 200, 320, False), ("password", 280, 460, False)
    ]
    for name, x, y, key in at_users:
        pos = draw_attribute(c, x, y, name, key=key)
        connect(c, user_pos, pos)

    # StudentDetails Attributes
    at_stud = [
        ("id", 420, 480, True), ("user_id (FK)", 580, 480, False),
        ("enrollment_no", 500, 500, False), ("phone", 420, 320, False),
        ("dob", 500, 300, False), ("profile_image", 580, 320, False), ("address", 500, 260, False)
    ]
    for name, x, y, key in at_stud:
        pos = draw_attribute(c, x, y, name, key=key)
        connect(c, student_pos, pos)

    # Enrollment Attributes
    at_enr = [
        ("id", 720, 480, True), ("student_id (FK)", 800, 500, False),
        ("course_id (FK)", 880, 480, False), ("status", 920, 400, False),
        ("date_enrolled", 920, 350, False)
    ]
    for name, x, y, key in at_enr:
        pos = draw_attribute(c, x, y, name, key=key)
        connect(c, enroll_pos, pos)

    # Course Attributes
    at_course = [
        ("id", 700, 150, True), ("name", 720, 100, False),
        ("course_code", 800, 50, False), ("credits", 880, 100, False),
        ("seats", 900, 150, False), ("description", 800, 220, False), ("link", 680, 200, False),
        ("fee", 920, 200, False), ("category", 920, 230, False),
        ("level", 920, 100, False), ("stream", 920, 130, False)
    ]
    for name, x, y, key in at_course:
        pos = draw_attribute(c, x, y, name, key=key)
        connect(c, course_pos, pos)

    c.save()
    print(f"ER Diagram PDF generated: {os.path.abspath(pdf_file)}")

if __name__ == "__main__":
    create_er_diagram()
