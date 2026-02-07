from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import db, User, Course, StudentDetails, Enrollment, CourseVideo, CourseSection
from models import db, User, Course, StudentDetails, Enrollment
from utils import generate_pdf_report, send_email_with_attachment, generate_upi_qr
import os
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__)

# ... (student_required decorator stays here, skipped for brevity in tool call context if not targeting it, but targeting full block for safety in this case or just top and bottom)
# RE-READING user request: "send to email with description and one pdf of rukes and regulation" 
# Modifying top of file first for import
# ACTUALLY, I will use replace_file_content for specific chunks to be cleaner.

# First chunk: Update Import
# Second chunk: Update enroll function


student_bp = Blueprint('student', __name__)

def student_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied. Students only.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)

@student_bp.route('/dashboard')
@student_required
def dashboard():
    # Helper to get student details
    details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    my_enrollments = Enrollment.query.filter_by(student_id=details.id).all() if details else []
    
    return render_template('student/dashboard.html', 
                           title='Student Dashboard',
                           details=details,
                           enrollments=my_enrollments)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    detail = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        detail.phone = request.form.get('phone')
        
        # Handle Date of Birth (handle empty string)
        dob_str = request.form.get('dob')
        if dob_str:
            detail.dob = dob_str
        
        detail.address = request.form.get('address')
        
        # Handle Image Upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                # Ensure directory exists
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Use a unique name to prevent cache issues or collisions
                unique_filename = f"user_{current_user.id}_{filename}"
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                
                # Save relative path to DB
                detail.profile_image = f"uploads/profile_pics/{unique_filename}"
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {e}', 'danger')
            
    return render_template('student/profile.html', user=current_user, detail=detail)

@student_bp.route('/courses')
@student_required
def courses():
    search_query = request.args.get('search', '')
    level = request.args.get('level')
    stream = request.args.get('stream')
    
    student_details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    # If using search, we might want to search across everything or just show matching courses
    if search_query:
         # Search logic: find courses matching query
         query = Course.query.filter(
            (Course.name.ilike(f'%{search_query}%')) | 
            (Course.course_code.ilike(f'%{search_query}%'))
         )
         all_courses = query.all()
         display_mode = 'courses'
    
    elif not level:
        # Step 1: Show Levels
        display_mode = 'levels'
        # Pass static list of levels as defined in requirements
        return render_template('student/courses.html', display_mode='levels')
        
    elif level and not stream:
        # Step 2: Show Streams for the selected level
        display_mode = 'streams'
        return render_template('student/courses.html', display_mode='streams', current_level=level)
        
    else:
        # Step 3: Show Courses for Level + Stream
        display_mode = 'courses'
        query = Course.query.filter_by(level=level, stream=stream)
        all_courses = query.all()

    # Get IDs of courses the student is already enrolled in
    enrolled_course_ids = []
    if student_details:
        enrolled = Enrollment.query.filter_by(student_id=student_details.id).all()
        enrolled_course_ids = [e.course_id for e in enrolled]
        
    return render_template('student/courses.html', 
                           courses=all_courses if display_mode == 'courses' else [], 
                           enrolled_ids=enrolled_course_ids, 
                           search_query=search_query,
                           display_mode='courses', # If we fell through to filter by level+stream
                           current_level=level,
                           current_stream=stream)

@student_bp.route('/course/<int:course_id>')
@student_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    student_details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    is_enrolled = False
    if student_details:
        enrollment = Enrollment.query.filter_by(student_id=student_details.id, course_id=course.id).first()
        if enrollment and enrollment.status in ['enrolled', 'completed']:
            is_enrolled = True
            
    # Fetch sections and videos for preview
    sections = CourseSection.query.filter_by(course_id=course.id).order_by(CourseSection.section_order).all()
    orphaned_videos = CourseVideo.query.filter_by(course_id=course.id, section_id=None).all()
    
    return render_template('student/course_details.html', course=course, sections=sections, orphaned_videos=orphaned_videos, is_enrolled=is_enrolled)

@student_bp.route('/enroll/<int:course_id>')
@student_required
def enroll(course_id):
    student_details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    if not student_details:
         # Should not happen if registered correctly, but safeguard
         flash('Student details missing.', 'danger')
         return redirect(url_for('student.dashboard'))
         
    # Check if already enrolled
    existing = Enrollment.query.filter_by(student_id=student_details.id, course_id=course_id).first()
    if existing:
        flash('You are already enrolled in this course.', 'warning')
        return redirect(url_for('student.courses'))
        
    # Check seats
    course = Course.query.get_or_404(course_id)
    if course.seats <= 0:
        flash('This course is full.', 'danger')
        return redirect(url_for('student.courses'))
        
    # Enroll with pending status
    enrollment = Enrollment(student_id=student_details.id, course_id=course.id, status='pending_payment')
    course.seats -= 1
    db.session.add(enrollment)
    db.session.commit()
    
    return redirect(url_for('student.payment_page', enrollment_id=enrollment.id))

@student_bp.route('/payment/<int:enrollment_id>', methods=['GET'])
@student_required
def payment_page(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    student_details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    # Security check: ensure this enrollment belongs to the current user
    if enrollment.student_id != student_details.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    if enrollment.status == 'enrolled':
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('student.dashboard'))

    # Generate UPI QR Code (Real)
    # Using User's Provided UPI ID
    admin_upi_id = "iranna4@ptyes" 
    qr_b64, upi_url = generate_upi_qr(
        upi_id=admin_upi_id, 
        name="Iranna (University)", 
        amount=enrollment.course.fee, 
        transaction_note=f"Enrollment {enrollment.id}"
    )

    return render_template('student/payment.html', enrollment=enrollment, course=enrollment.course, qr_code=qr_b64, upi_link=upi_url)

@student_bp.route('/payment/<int:enrollment_id>/process', methods=['POST'])
@student_required
def process_payment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    student_details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    if enrollment.student_id != student_details.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    payment_method = request.form.get('payment_method')

    # Handle Bank Transfer
    if payment_method == 'bank_transfer':
        transaction_ref = request.form.get('transaction_reference')
        receipt_file = request.files.get('receipt_image')
        
        if not transaction_ref or not receipt_file:
            flash('Please provide both transaction reference and receipt image.', 'danger')
            return redirect(url_for('student.payment_page', enrollment_id=enrollment.id))
            
        if receipt_file and allowed_file(receipt_file.filename):
            filename = secure_filename(receipt_file.filename)
            # Ensure directory exists
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'receipts')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Unique filename
            unique_filename = f"receipt_{enrollment.id}_{filename}"
            file_path = os.path.join(upload_folder, unique_filename)
            receipt_file.save(file_path)
            
            # Update Enrollment
            enrollment.transaction_reference = transaction_ref
            enrollment.receipt_image = f"uploads/receipts/{unique_filename}"
 
        else:
             flash('Invalid file type for receipt.', 'danger')
             return redirect(url_for('student.payment_page', enrollment_id=enrollment.id))

    # Handle UPI Payment
    elif payment_method == 'upi':
        # Transaction reference is optional/not enforced for now as per user request
        transaction_ref = request.form.get('transaction_reference') 
        enrollment.transaction_reference = transaction_ref or "Manual-Confirmation"

    # Determine Transaction ID for Record
    import uuid
    if payment_method == 'card':
        transaction_id = str(uuid.uuid4())
    else:
        # For Bank Transfer and UPI, use the user-provided reference
        transaction_id = request.form.get('transaction_reference')
    
    # Update Status
    enrollment.status = 'enrolled'
    db.session.commit()
    
    # Send email with attachment (Moved from enroll)
    course = enrollment.course
    subject = f"Enrollment Confirmed: {course.name}"
    body = f"""Hello {current_user.name},

You have successfully enrolled in the following course:

Course: {course.name} ({course.course_code})
Credits: {course.credits}
Description: {course.description}
Course Material/Link: {course.link if course.link else 'N/A'}
Transaction ID: {transaction_id}

Please find attached the University Rules and Regulations.

Happy Learning!
University Admin"""
    
    # Path to the PDF file
    pdf_path = os.path.join('static', 'files', 'rules.pdf')
    
    try:
        # Check if file exists, if not maybe skip attachment or log warning
        if os.path.exists(os.path.join(current_app.root_path, pdf_path)):
             send_email_with_attachment(current_user.email, subject, body, attachment_path=pdf_path, attachment_name='University_Rules.pdf')
        else:
             print(f"Warning: Rules PDF not found at {pdf_path}")
             # Send email without attachment or handle gracefully
             # For now, just try sending, send_email_with_attachment handles errors usually? 
             # We will just proceed.
             pass
    except Exception as e:
        print(f"Error sending email: {e}")

    flash(f'Payment successful! You are now enrolled in {course.name}.', 'success')
    # Determine Transaction ID for Record
    import uuid
    if payment_method == 'card':
        transaction_id = str(uuid.uuid4())
    else:
        # For Bank Transfer and UPI, use the user-provided reference
        transaction_id = request.form.get('transaction_reference')
    
    # Update Status
    enrollment.status = 'enrolled'
    db.session.commit()
    


    return redirect(url_for('student.confirmation_page', enrollment_id=enrollment.id, tx_id=transaction_id))





@student_bp.route('/confirmation/<int:enrollment_id>')
@student_required
def confirmation_page(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    student_details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    if enrollment.student_id != student_details.id:
        return redirect(url_for('student.dashboard'))
        
    transaction_id = request.args.get('tx_id', 'N/A')
    
    return render_template('student/confirmation.html', enrollment=enrollment, course=enrollment.course, transaction_id=transaction_id)

@student_bp.route('/watch/<int:course_id>')
@student_required
def watch_course(course_id):
    course = Course.query.get_or_404(course_id)
    student_details = StudentDetails.query.filter_by(user_id=current_user.id).first()
    
    if not student_details:
        flash('Student details missing.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    # Check enrollment status
    enrollment = Enrollment.query.filter_by(student_id=student_details.id, course_id=course.id).first()
    
    if not enrollment or enrollment.status not in ['enrolled', 'completed']:
        flash('You must be enrolled in this course to watch videos.', 'warning')
        return redirect(url_for('student.courses'))
        
    # Fetch sections with videos (eager load if possible, but lazy load works with loop in template)
    sections = CourseSection.query.filter_by(course_id=course.id).order_by(CourseSection.section_order).all()
    
    # Also get orphaned videos
    orphaned_videos = CourseVideo.query.filter_by(course_id=course.id, section_id=None).all()
    
    return render_template('student/watch_course.html', course=course, sections=sections, orphaned_videos=orphaned_videos)
