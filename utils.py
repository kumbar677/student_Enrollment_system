from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64

try:
    import qrcode
except ImportError:
    qrcode = None

def generate_upi_qr(upi_id, name, amount, transaction_note="Enrollment Fee"):
    """
    Generates a UPI QR code and returns as base64 string.
    UPI URL Format: upi://pay?pa=<upi_id>&pn=<name>&am=<amount>&tn=<note>
    """
    # Ensure amount is string with 2 decimals
    amount_str = "{:.2f}".format(float(amount))
    
    # Construct UPI URL
    # standardized UPI deep link format
    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount_str}&tn={transaction_note}&cu=INR"
    
    # Try local generation
    if qrcode:
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(upi_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}", upi_url
        except Exception as e:
            print(f"Local QR generation failed: {e}")
            pass
            
    # Fallback to Online API (Robust fix)
    import urllib.parse
    encoded_url = urllib.parse.quote(upi_url)
    api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_url}"
    return api_url, upi_url

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape

def generate_pdf_report(data, title="Report"):
    """
    Generates a PDF report with a table.
    data: List of lists, where the first list is the header row.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    if data:
        # Create Table
        table = Table(data)
        
        # Style the Table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ])
        
        # Add alternating row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.beige
            style.add('BACKGROUND', (0, i), (-1, i), bg_color)
            
        table.setStyle(style)
        elements.append(table)
    else:
        elements.append(Paragraph("No data available to display.", styles['Normal']))
        
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

from flask_mail import Message
from flask import current_app

def send_email_with_attachment(to_email, subject, body, attachment_path=None, attachment_name='document.pdf'):
    """
    Sends an email using Flask-Mail.
    """
    try:
        msg = Message(subject, recipients=[to_email])
        msg.body = body
        msg.sender = current_app.config.get('MAIL_USERNAME')
        
        if attachment_path:
            with current_app.open_resource(attachment_path) as fp:
                msg.attach(attachment_name, "application/pdf", fp.read())
        
        mail = current_app.extensions.get('mail')
        if mail:
            mail.send(msg)
            print(f"Email sent to {to_email}")
            return True
        else:
            print("Mail extension not found.")
            return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
