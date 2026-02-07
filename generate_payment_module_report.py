from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, PageBreak, Preformatted, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_payment_report():
    pdf_file = "Payment_Module_Report.pdf"
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
    # PAGE 1: TITLE & EXECUTIVE SUMMARY
    # ==========================
    story.append(Paragraph("Student Enrollment System", title_style))
    story.append(Paragraph("Payment Module Implementation Report", h2_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>Date:</b> January 16, 2026", normal_style))
    story.append(Paragraph("<b>Module:</b> Real UPI Payment Integration", normal_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>1. Executive Summary</b>", h1_style))
    story.append(Paragraph("This report documents the successful implementation of the Real UPI Payment Module. The system now supports dynamic course fees and generates scannable QR codes for direct payments via PhonePe, Google Pay, and Paytm.", normal_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Key Features Delivered:</b>", h3_style))
    features = [
        "<b>Dynamic Course Fees:</b> Admins can set specific fees for each course.",
        "<b>Real UPI QR Code:</b> Generates valid `upi://` QR codes for scanning.",
        "<b>Deep Linking:</b> Mobile buttons to open PhonePe/GPay directly.",
        "<b>Robust Fallback:</b> Uses Online QR API if local libraries fail.",
        "<b>Transaction Simulation:</b> 'I Have Paid' confirmation flow."
    ]
    story.append(ListFlowable([ListItem(Paragraph(f, normal_style)) for f in features], bulletType='bullet'))
    story.append(PageBreak())

    # ==========================
    # PAGE 2: IMPLEMENTATION DETAILS
    # ==========================
    story.append(Paragraph("2. Technical Implementation", h1_style))
    
    # Database Changes
    story.append(Paragraph("<b>A. Database Schema Changes</b>", h2_style))
    story.append(Paragraph("Modified the schema to support fees and payment status.", normal_style))
    db_data = [
        ["Table", "Change", "Description"],
        ["courses", "Added `fee` (FLOAT)", "Stores course price (Default: 500.0)."],
        ["enrollments", "Status Update", "Added 'pending_payment' status logic."]
    ]
    t_db = Table(db_data, colWidths=[100, 150, 200])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.navy),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 15))

    # Package Installation
    story.append(Paragraph("<b>B. Infrastructure & Packages</b>", h2_style))
    story.append(Paragraph("New Python libraries installed to support QR generation.", normal_style))
    pkg_data = [
        ["Package", "Purpose", "Installation Command"],
        ["qrcode[pil]", "Generates QR code images locally.", "pip install qrcode[pil]"],
        ["pillow", "Image processing dependency.", "pip install pillow"]
    ]
    t_pkg = Table(pkg_data, colWidths=[100, 150, 200])
    t_pkg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkgreen),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    story.append(t_pkg)
    story.append(PageBreak())

    # ==========================
    # PAGE 3: WORKFLOW & CODE LOGIC
    # ==========================
    story.append(Paragraph("3. Payment Workflow Logic", h1_style))
    
    story.append(Paragraph("<b>Step 1: Enrollment</b>", h3_style))
    story.append(Paragraph("User clicks 'Enroll'. System creates an Enrollment record with `status='pending_payment'`.", normal_style))
    
    story.append(Paragraph("<b>Step 2: Payment Page</b>", h3_style))
    story.append(Paragraph("User is redirected to `/student/payment/<id>`. The system:", normal_style))
    steps = [
        "Fetches the Course Fee.",
        "Generates a UPI Deep Link: `upi://pay?pa=iranna4@ptyes&...`",
        "Generates a QR Code image (Locally or via fallback API).",
        "Displays 'Pay via PhonePe/GPay' buttons."
    ]
    story.append(ListFlowable([ListItem(Paragraph(s, normal_style)) for s in steps], bulletType='bullet'))
    
    story.append(Paragraph("<b>Step 3: Confirmation</b>", h3_style))
    story.append(Paragraph("User pays via App -> Clicks 'I Have Paid'.", normal_style))
    story.append(Paragraph("System updates status to 'enrolled', sends confirmation email with Invoice/Rules PDF.", normal_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Configuration: Changing the UPI ID</b>", h2_style))
    story.append(Paragraph("To change the recipient bank account, edit `routes/student_routes.py`:", normal_style))
    code_snippet = """
    # Inside routes/student_routes.py
    
    # Using User's Provided UPI ID
    admin_upi_id = "iranna4@ptyes"  # <-- CHANGE THIS VAULE
    
    qr_b64, upi_url = generate_upi_qr(
        upi_id=admin_upi_id,
        ...
    )
    """
    story.append(Preformatted(code_snippet, code_style))
    story.append(PageBreak())

    # ==========================
    # PAGE 4: COMMAND LOG (PROMPTS & ACTIONS)
    # ==========================
    story.append(Paragraph("4. Session Command Log", h1_style))
    story.append(Paragraph("Chronological list of key actions taken during this session.", normal_style))
    
    cmd_data = [
        ["Action Type", "Details"],
        ["Prompt", "User: 'make Real UPI Payment Integration'"],
        ["Coding", "Added `fee` column to models & database."],
        ["Coding", "Created `payment.html` & `confirmation.html`."],
        ["Command", "python -m pip install qrcode pillow"],
        ["Debugging", "Fixed `BuildError` in auth.login (Blueprints)."],
        ["Debugging", "Fixed `No module named qrcode` crash."],
        ["Debugging", "Fixed 'Invalid UPI ID' error (Updated to 'iranna4@ptyes')."],
        ["Verification", "Tested QR Code generation and display."]
    ]
    t_cmd = Table(cmd_data, colWidths=[100, 350])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_cmd)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>End of Report</b>", normal_style))

    doc.build(story)
    print(f"Report generated: {os.path.abspath(pdf_file)}")

if __name__ == "__main__":
    create_payment_report()
