
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfgen import canvas
import os

def draw_entity(c, x, y, name, width=100, height=50):
    """ External Entity (Source/Sink) - Rectangle """
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.rect(x - width/2, y - height/2, width, height, fill=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x, y - 5, name)
    return (x, y, width, height)

def draw_process(c, x, y, name, width=120, height=60):
    """ Process - Rounded Rectangle """
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.lightyellow)
    c.roundRect(x - width/2, y - height/2, width, height, 15, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    # Split text if too long
    words = name.split()
    if len(words) > 2:
        c.drawCentredString(x, y + 5, " ".join(words[:2]))
        c.drawCentredString(x, y - 10, " ".join(words[2:]))
    else:
        c.drawCentredString(x, y - 4, name)
    return (x, y, width, height)

def draw_datastore(c, x, y, name, width=100, height=40):
    """ Data Store - Open Rectangle (Two horizontal lines + one vertical left) """
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    
    # Left vertical
    c.line(x - width/2, y - height/2, x - width/2, y + height/2)
    # Top horizontal
    c.line(x - width/2, y + height/2, x + width/2, y + height/2)
    # Bottom horizontal
    c.line(x - width/2, y - height/2, x + width/2, y - height/2)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(x, y - 4, name)
    return (x, y, width, height)

def draw_flow(c, p1, p2, label=""):
    """ Arrow connection """
    # Simple logic to connect boundaries
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    
    # Adjust start/end points to touch edges of objects (approx)
    dx = x2 - x1
    dy = y2 - y1
    
    c.setStrokeColor(colors.black)
    c.line(x1, y1, x2, y2)
    
    # Arrow head
    import math
    angle = math.atan2(dy, dx)
    arrow_len = 10
    angle1 = angle + math.pi/6
    angle2 = angle - math.pi/6
    
    # End point
    ax1 = x2 - arrow_len * math.cos(angle1)
    ay1 = y2 - arrow_len * math.sin(angle1)
    ax2 = x2 - arrow_len * math.cos(angle2)
    ay2 = y2 - arrow_len * math.sin(angle2)
    
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(ax1, ay1)
    p.lineTo(ax2, ay2)
    p.close()
    c.setFillColor(colors.black)
    c.drawPath(p, fill=1, stroke=1)
    
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        c.setFillColor(colors.white)
        c.rect(mid_x - 30, mid_y - 5, 60, 10, fill=1, stroke=0) # Text BG
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 8)
        c.drawCentredString(mid_x, mid_y - 2, label)

def create_dfd():
    pdf_file = "Data_Flow_Diagram.pdf"
    c = canvas.Canvas(pdf_file, pagesize=landscape(A3))
    width, height = landscape(A3)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 50, "Level 1 Data Flow Diagram (DFD)")
    
    # --- LEVEL 1 DFD LAYOUT ---
    
    # Entities
    student_ent = draw_entity(c, 100, 500, "Student")
    admin_ent = draw_entity(c, 100, 200, "Admin")
    
    # Processes
    login_proc = draw_process(c, 300, 350, "1.0 Auth/Login")
    browse_proc = draw_process(c, 450, 500, "2.0 Browse Courses")
    enroll_proc = draw_process(c, 650, 500, "3.0 Enroll/Pay")
    admin_proc = draw_process(c, 450, 200, "4.0 Manage Courses/Students")
    
    # Data Stores
    user_db = draw_datastore(c, 300, 250, "D1 Users")
    course_db = draw_datastore(c, 600, 350, "D2 Courses")
    enroll_db = draw_datastore(c, 800, 350, "D3 Enrollments")
    
    # --- FLOWS ---
    
    # Auth Flows
    draw_flow(c, (student_ent[0]+50, student_ent[1]), (login_proc[0]-60, login_proc[1]), "Creds")
    draw_flow(c, (admin_ent[0]+50, admin_ent[1]), (login_proc[0]-60, login_proc[1]), "Creds")
    draw_flow(c, (login_proc[0], login_proc[1]-30), (user_db[0], user_db[1]+20), "Validate")
    
    # Student Flows
    draw_flow(c, (student_ent[0]+50, student_ent[1]+10), (browse_proc[0]-60, browse_proc[1]), "Filter Stream")
    draw_flow(c, (course_db[0]-20, course_db[1]+20), (browse_proc[0]+30, browse_proc[1]-20), "Course Data")
    
    draw_flow(c, (browse_proc[0]+60, browse_proc[1]), (enroll_proc[0]-60, enroll_proc[1]), "Select Course")
    draw_flow(c, (enroll_proc[0], enroll_proc[1]-30), (enroll_db[0], enroll_db[1]+20), "Save Enrollment")
    draw_flow(c, (enroll_proc[0]-20, enroll_proc[1]-30), (course_db[0], course_db[1]+20), "Check Seats")
    
    # Admin Flows
    draw_flow(c, (admin_ent[0]+50, admin_ent[1]), (admin_proc[0]-60, admin_proc[1]), "Add Course/Video")
    draw_flow(c, (admin_proc[0]+30, admin_proc[1]+30), (course_db[0]-20, course_db[1]-20), "Update Info")
    draw_flow(c, (admin_proc[0]+60, admin_proc[1]), (enroll_db[0], enroll_db[1]-20), "View Reports")
    draw_flow(c, (admin_proc[0]-30, admin_proc[1]+30), (user_db[0]+30, user_db[1]-20), "Manage Users")

    c.save()
    print(f"DFD PDF generated: {os.path.abspath(pdf_file)}")

if __name__ == "__main__":
    create_dfd()
