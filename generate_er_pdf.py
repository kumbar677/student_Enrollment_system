from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.graphics.shapes import Drawing, Rect, Ellipse, Line, String, Polygon
from reportlab.graphics import renderPDF

def draw_chen_er_diagram():
    pdf_file = "ER_Diagram.pdf"
    # Create a drawing canvas
    width, height = landscape(letter)
    d = Drawing(width, height)
    
    # --- Helper Functions ---
    def draw_entity(x, y, w, h, text, color=colors.lightblue):
        # Rectangle
        r = Rect(x, y, w, h, fillColor=color, strokeColor=colors.black)
        d.add(r)
        # Text centered
        s = String(x + w/2, y + h/2 - 4, text, textAnchor='middle', fontName='Helvetica-Bold', fontSize=12)
        d.add(s)
        return (x + w/2, y + h/2, x, y, w, h) # Return center and bounds

    def draw_relationship(cx, cy, size, text, color=colors.lightgrey):
        # Diamond (Polygon)
        half = size / 2
        p_points = [cx, cy + half, cx + half, cy, cx, cy - half, cx - half, cy]
        dia = Polygon(p_points, fillColor=color, strokeColor=colors.black)
        d.add(dia)
        s = String(cx, cy - 4, text, textAnchor='middle', fontName='Helvetica-Bold', fontSize=10)
        d.add(s)
        return (cx, cy)

    def draw_attribute(cx, cy, rx, ry, text, parent_center):
        # Oval
        e = Ellipse(cx, cy, rx, ry, fillColor=colors.white, strokeColor=colors.black)
        d.add(e)
        s = String(cx, cy - 3, text, textAnchor='middle', fontSize=8)
        d.add(s)
        # Line to parent
        l = Line(cx, cy, parent_center[0], parent_center[1], strokeColor=colors.black)
        # Add line first to be behind? No, adds to end. We want lines behind usually, but this is simple.
        # Ideally insert line at beginning of list or Draw logic. For now, just add.
        d.contents.insert(0, l) 

    def connect(center1, center2, label=""):
        l = Line(center1[0], center1[1], center2[0], center2[1], strokeColor=colors.black, strokeWidth=1.5)
        d.contents.insert(0, l)
        if label:
            mid_x = (center1[0] + center2[0]) / 2
            mid_y = (center1[1] + center2[1]) / 2
            s = String(mid_x, mid_y + 5, label, textAnchor='middle', fontSize=9, fillColor=colors.red)
            d.add(s)

    # --- Layout Logic ---
    center_x = width / 2
    center_y = height / 2
    
    # 1. ENTITIES (Rectangles)
    # Student (Left)
    student_c = draw_entity(100, center_y - 25, 100, 50, "Student")
    
    # Course (Right)
    course_c = draw_entity(width - 200, center_y - 25, 100, 50, "Course")
    
    # 2. RELATIONSHIP (Diamond)
    # Enrolls (Center) - Representing Enrollment & Payment
    enroll_c = draw_relationship(center_x, center_y, 80, "Enrolls")
    
    # Connect them
    connect((student_c[0], student_c[1]), enroll_c, "1") # 1 Student
    connect((course_c[0], course_c[1]), enroll_c, "N")  # N Courses (or M:N actually)
    
    # 3. ATTRIBUTES (Ovals)
    
    # Student Attributes
    draw_attribute(150, center_y + 80, 40, 20, "Name", student_c)
    draw_attribute(80, center_y + 80, 40, 20, "Email", student_c)
    draw_attribute(150, center_y - 80, 40, 20, "ID (PK)", student_c) # PK

    # Course Attributes
    draw_attribute(width - 150, center_y + 80, 40, 20, "Name", course_c)
    draw_attribute(width - 220, center_y + 80, 40, 20, "Credits", course_c)
    # FEE (Important)
    draw_attribute(width - 150, center_y - 80, 40, 20, "Fee", course_c)
    
    # ENROLLMENT / PAYMENT ATTRIBUTES (Connected to Relationship)
    # This is the key part for "Payment ER Diagram"
    
    # Status
    draw_attribute(center_x, center_y + 80, 50, 25, "Status", enroll_c)
    
    # PAYMENTS
    draw_attribute(center_x - 60, center_y - 80, 60, 25, "Transaction Ref", enroll_c)
    draw_attribute(center_x + 60, center_y - 80, 50, 25, "Receipt Img", enroll_c)
    draw_attribute(center_x, center_y - 120, 50, 25, "Date", enroll_c)

    # Title
    title = String(center_x, height - 50, "ER Diagram - Payment Integration (Chen Notation)", 
                   textAnchor='middle', fontName='Helvetica-Bold', fontSize=18)
    d.add(title)

    # Render
    renderPDF.drawToFile(d, pdf_file, 'ER Diagram')
    print(f"Chen Notation ER Diagram generated: {pdf_file}")

if __name__ == "__main__":
    draw_chen_er_diagram()
