
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def create_project_description_pdf(filename="ACI_Project_Description.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    Story = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=18, spaceAfter=20))
    
    # Title
    title = "Student Enrollment System - Project Overview"
    Story.append(Paragraph(title, styles["Center"]))
    Story.append(Spacer(1, 12))
    
    # Content based on user's request (adapted for Enrollment System)
    # Section 1: Introduction / Problem Statement
    text1 = """
    Doing enrollment by hand causes many problems. It is slow and mistakes happen often. 
    Key issues include wrong data, hard-to-find records, and no central place to manage everything. 
    Without a computer system, schools struggle to track student forms, check if classes are full, 
    and see who has paid fees. Also, making reports and checking student details takes a lot of time.
    """
    
    # Section 2: Existing System Limitations (Adapted from user request)
    subtitle_existing = "Existing System"
    text_existing = """
    The old way of working relies on paper notebooks and simple Excel sheets. While this might suffice 
    for a small school, it fails as the number of students grows. Staff face hard times trying to 
    find old records or handle many admissions at the same time.
    
    Also, paper papers can get lost, torn, or stolen. This is dangerous for student privacy and 
    can cause the college to lose money or mix up important details. There is no easy way to see 
    live updates on which student is in which class or where the drivers (in this case, students/faculty) are.
    
    Other big problems include:
    1. No automatic fee calculation: Staff spend hours doing math and often make mistakes.
    2. Slow information: Finding student or course details takes too long, making decisions slow 
       and keeping everyone waiting.
    """
    
    # Section 3: Proposed Solution
    subtitle_proposed = "Proposed System (ACI)"
    text2 = """
    By using the <b>Annual Course Intake (ACI) System</b>, these problems are solved. 
    This system makes everything run smoothly by doing the hard work automatically. 
    It stops mistakes and makes things much easier and faster for both students and staff.
    """
    
    # Section 4: Cost Effectiveness (Adapted from user request)
    subtitle_cost = "Why it Saves Money (Cost Effectiveness)"
    text_cost = """
    Building this project with Python and MySQL is very cheap because these tools are free. 
    We do not need to buy expensive software licenses.
    
    Also, the system saves money every day. Staff do not need to spend hours doing manual data entry 
    or fixing mistakes. We save costs on paper, printing, and storing big files. Because the work 
    finishes faster, the college works better and saves money in the long run. It is a smart financial choice.
    """
    
    # Add paragraphs
    Story.append(Paragraph(text1, styles["Justify"]))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph(subtitle_existing, styles["Heading2"]))
    Story.append(Paragraph(text_existing, styles["Justify"]))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph(subtitle_proposed, styles["Heading2"]))
    Story.append(Paragraph(text2, styles["Justify"]))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph(subtitle_cost, styles["Heading2"]))
    Story.append(Paragraph(text_cost, styles["Justify"]))
    
    # Build
    doc.build(Story)
    print(f"PDF generated successfully: {filename}")

if __name__ == "__main__":
    create_project_description_pdf()
