from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, PageBreak, Preformatted, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_workflow_report():
    pdf_file = "Project_Workflow_Architecture.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # --- Styles ---
    title_style = styles['Title']
    h1_style = styles['Heading1']
    h2_style = styles['Heading2']
    h3_style = styles['Heading3']
    normal_style = styles['BodyText']
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['BodyText'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        backColor=colors.whitesmoke,
        borderPadding=5,
        spaceAfter=5
    )

    # ==========================
    # PAGE 1: TITLE & OVERVIEW
    # ==========================
    story.append(Paragraph("University Enrollment System", title_style))
    story.append(Paragraph("Full Stack Project Operational Workflow", h2_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>Date:</b> January 16, 2026", normal_style))
    story.append(Paragraph("<b>System Type:</b> Flask (Python) Full Stack Web Application", normal_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>1. System Overview</b>", h1_style))
    story.append(Paragraph("This application is a comprehensive university management portal designed to streamline the student enrollment process. It features a secure Role-Based Access Control (RBAC) system distinguishing between Administrators and Students.", normal_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Core Capabilities:</b>", h3_style))
    caps = [
        "<b>Secure Authentication:</b> Hashed passwords, Session management, Login decorators.",
        "<b>Admin Dashboard:</b> Course CRUD, Student Management, Analytics.",
        "<b>Student Portal:</b> Profile management, Course Browsing, Self-Enrollment.",
        "<b>Payments:</b> Real-time UPI integration with QR generation.",
        "<b>Notifications:</b> Automated Email confirmations with PDF attachments."
    ]
    story.append(ListFlowable([ListItem(Paragraph(c, normal_style)) for c in caps], bulletType='bullet'))
    story.append(PageBreak())

    # ==========================
    # PAGE 2: USER WORKFLOWS (AUTH & ADMIN)
    # ==========================
    story.append(Paragraph("2. User Workflows", h1_style))
    
    # Auth Flow
    story.append(Paragraph("<b>A. Authentication Module</b>", h2_style))
    story.append(Paragraph("entry point for all users.", normal_style))
    auth_flow = [
        "<b>Registration:</b> New users sign up as 'Student'. System auto-generates an Enrollment Number (e.g., UNIV2026001).",
        "<b>Login:</b> Users input Email/Password. System authenticates hash and checks Role.",
        "<b>Routing:</b> Admins redirect to `/admin/dashboard`. Students redirect to `/student/dashboard`."
    ]
    story.append(ListFlowable([ListItem(Paragraph(f, normal_style)) for f in auth_flow], bulletType='bullet'))
    story.append(Spacer(1, 15))

    # Admin Flow
    story.append(Paragraph("<b>B. Admin Workflow</b>", h2_style))
    story.append(Paragraph("Authorized personnel manage the academic data.", normal_style))
    admin_steps = [
        "<b>Dashboard View:</b> See quick stats (Total Students, Courses, Recent Enrollments).",
        "<b>Manage Courses:</b> Create new courses (Set Name, Code, Fee, Seats). Edit existing details.",
        "<b>Manage Students:</b> View all registered students. Delete unauthorized accounts.",
        "<b>System Oversight:</b> Monitor database integrity and enrollment logs."
    ]
    story.append(ListFlowable([ListItem(Paragraph(s, normal_style)) for s in admin_steps], bulletType='bullet'))
    story.append(PageBreak())

    # ==========================
    # PAGE 3: STUDENT JOURNEY (ENROLLMENT & PAYMENT)
    # ==========================
    story.append(Paragraph("<b>C. Student Journey (End-to-End)</b>", h2_style))
    story.append(Paragraph("The primary lifecycle of a student user.", normal_style))
    
    # Workflow Diagram (Textual)
    flow_data = [
        ["Phase", "Action", "System Process"],
        ["1. Profile", "Update Info", "Uploads Profile Pic, sets Phone/Address."],
        ["2. Discovery", "View Courses", "Browse available courses. Filter by name."],
        ["3. Action", "Click 'Enroll'", "Checks Seat Availability. Creates 'Pending' Enrollment."],
        ["4. Payment", "Scan QR Code", "Generates UPI Link. User pays via PhonePe/GPay."],
        ["5. Confirm", "Click 'Paid'", "Updates Status -> 'Enrolled'. Decrements Seats."],
        ["6. Receipt", "Receive Email", "System mails 'Enrollment Confirmed' + Rules.pdf."]
    ]
    t_flow = Table(flow_data, colWidths=[80, 100, 250])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.teal),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_flow)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>Key Technical Highlight: Payment Integration</b>", h3_style))
    story.append(Paragraph("The payment system uses a hybrid approach for maximum reliability:", normal_style))
    story.append(Paragraph("1. <b>Dynamic Generation:</b> Calculates Fee from DB.", normal_style))
    story.append(Paragraph("2. <b>Deep Linking:</b> `upi://pay?...` allows one-tap mobile payments.", normal_style))
    story.append(Paragraph("3. <b>Dual Rendering:</b> Uses local `qrcode` library, falls back to `qrserver.com` API if local fails.", normal_style))
    story.append(PageBreak())

    # ==========================
    # PAGE 4: ARCHITECTURE & DATABASE
    # ==========================
    story.append(Paragraph("3. System Architecture", h1_style))
    
    story.append(Paragraph("<b>A. Database Schema (ERD Description)</b>", h2_style))
    db_schema = [
        ["Model", "Fields", "Relationships"],
        ["User", "id, name, email, password_hash, role", "One-to-One with StudentDetails"],
        ["Course", "id, name, code, fee, seats, credits", "One-to-Many with Enrollments"],
        ["Enrollment", "id, student_id, course_id, status", "Link Table (Many-to-Many logic)"]
    ]
    t_db = Table(db_schema, colWidths=[80, 200, 150])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>B. Application Structure</b>", h2_style))
    structure = """
    Pro_MCA/
    ├── app.py              # Application Factory & Entry Point
    ├── models.py           # Database Models (SQLAlchemy)
    ├── config.py           # Configuration (Secret Keys, DB URI)
    ├── utils.py            # Helpers (PDF, Email, QR Code)
    ├── routes/             # Blueprints (Modular Routing)
    │   ├── auth_routes.py    # Login/Register
    │   ├── admin_routes.py   # Admin Ops
    │   └── student_routes.py # Student Ops
    └── templates/          # HTML Frontend (Jinja2)
        ├── auth/           # Login Screens
        ├── admin/          # Dashboard & Forms
        └── student/        # Portal & Payment
    """
    story.append(Preformatted(structure, code_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Generated by AI Assistant.</b>", normal_style))

    doc.build(story)
    print(f"Workflow Report generated: {os.path.abspath(pdf_file)}")

if __name__ == "__main__":
    create_workflow_report()   