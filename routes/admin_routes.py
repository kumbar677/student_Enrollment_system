from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import db, User, Course, StudentDetails, Enrollment, CourseVideo, CourseSection
from utils import generate_pdf_report

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = User.query.filter_by(role='student').count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    
    return render_template('admin/dashboard.html', 
                           title='Admin Dashboard',
                           total_students=total_students,
                           total_courses=total_courses,
                           total_enrollments=total_enrollments)

@admin_bp.route('/students', methods=['GET', 'POST'])
@admin_required
def manage_students():
    search_query = request.args.get('search', '')
    query = db.session.query(User).join(StudentDetails, User.id == StudentDetails.user_id).filter(User.role == 'student')
    
    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        )
        
    students = query.all()
    return render_template('admin/students.html', students=students, search_query=search_query)

@admin_bp.route('/students/delete/<int:user_id>')
@admin_required
def delete_student(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'student':
        flash('Cannot delete non-student users from here.', 'warning')
        return redirect(url_for('admin.manage_students'))
        
    db.session.delete(user)
    db.session.commit()
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/courses', methods=['GET', 'POST'])
@admin_required
def manage_courses():
    if request.method == 'POST':
        try:
            course_code = request.form.get('course_code')
            name = request.form.get('name')
            credits = int(request.form.get('credits'))
            seats = int(request.form.get('seats'))
            description = request.form.get('description')
            link = request.form.get('link')
            fee = float(request.form.get('fee'))
            category = request.form.get('category', 'General')
            
            existing = Course.query.filter_by(course_code=course_code).first()
            if existing:
                flash('Course Code already exists.', 'warning')
            else:
                new_course = Course(
                    course_code=course_code, 
                    name=name, 
                    credits=credits, 
                    seats=seats, 
                    description=description, 
                    link=link,
                    fee=fee,
                    category=category,
                    level=request.form.get('level'),
                    stream=request.form.get('stream')
                )
                db.session.add(new_course)
                db.session.commit()
                flash('Course added successfully.', 'success')
            return redirect(url_for('admin.manage_courses'))
            
        except ValueError:
            flash('Invalid input for Fee, Credits, or Seats.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course: {e}', 'danger')
            
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

    return render_template('admin/courses.html', courses=courses)

    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/<int:course_id>/videos', methods=['GET', 'POST'])
@admin_required
def manage_course_videos(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        action = request.form.get('action') # 'add_section' or 'add_video'
        
        if action == 'add_section':
            title = request.form.get('title')
            order = request.form.get('section_order', 0)
            if title:
                section = CourseSection(course_id=course.id, title=title, section_order=order)
                db.session.add(section)
                db.session.commit()
                flash('Section created.', 'success')
            else:
                flash('Section title required.', 'danger')
        
        elif action == 'add_video':
            title = request.form.get('title')
            video_url = request.form.get('video_url')
            section_id = request.form.get('section_id') # Can be None if we allow uncategorized
            duration = request.form.get('duration')
            
            # Simple validation
            if title and video_url:
                vid = CourseVideo(
                    course_id=course.id,
                    title=title,
                    video_url=video_url,
                    section_id=section_id if section_id else None,
                    duration=duration
                )
                db.session.add(vid)
                db.session.commit()
                flash('Video added.', 'success')
            else:
                flash('Title and URL required.', 'danger')
            
        return redirect(url_for('admin.manage_course_videos', course_id=course.id))
        
    # Fetch sections ordered, and videos
    sections = CourseSection.query.filter_by(course_id=course.id).order_by(CourseSection.section_order).all()
    # Also fetch videos that might not be in a section (orphaned or legacy)
    # Strategy: We will attach videos to sections in the template or pre-process here
    # Actually, SQLA relationship 'sections' on Course does not eager load videos by default. 
    # Let's rely on relationships: section.videos
    
    orphaned_videos = CourseVideo.query.filter_by(course_id=course.id, section_id=None).all()
    
    return render_template('admin/manage_videos.html', course=course, sections=sections, orphaned_videos=orphaned_videos)

@admin_bp.route('/courses/sections/delete/<int:section_id>')
@admin_required
def delete_section(section_id):
    section = CourseSection.query.get_or_404(section_id)
    course_id = section.course_id
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted.', 'success')
    return redirect(url_for('admin.manage_course_videos', course_id=course_id))



@admin_bp.route('/courses/videos/delete/<int:video_id>')
@admin_required
def delete_course_video(video_id):
    video = CourseVideo.query.get_or_404(video_id)
    course_id = video.course_id
    db.session.delete(video)
    db.session.commit()
    flash('Video deleted.', 'success')
    return redirect(url_for('admin.manage_course_videos', course_id=course_id))

@admin_bp.route('/courses/delete/<int:course_id>')
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully.', 'success')
    return redirect(url_for('admin.manage_courses'))

@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.course_code = request.form.get('course_code')
        course.name = request.form.get('name')
        course.credits = request.form.get('credits')
        course.seats = request.form.get('seats')
        course.description = request.form.get('description')
        course.link = request.form.get('link')
        course.fee = request.form.get('fee')
        course.category = request.form.get('category', 'General')
        course.level = request.form.get('level')
        course.stream = request.form.get('stream')
        
        try:
            db.session.commit()
            flash('Course updated successfully.', 'success')
            return redirect(url_for('admin.manage_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {e}', 'danger')
            
    return render_template('admin/edit_course.html', course=course)

@admin_bp.route('/report')
@admin_required
def generate_report():
    enrollments = db.session.query(Enrollment, User, Course).select_from(Enrollment).join(StudentDetails).join(User).join(Course).all()
    
    # Header Row
    data = [['ID', 'Student Name', 'Email', 'Course', 'Code', 'Date', 'Status']]
    
    # Data Rows
    for enr, user, course in enrollments:
        data.append([
            str(enr.id),
            user.name,
            user.email,
            course.name,
            course.course_code,
            enr.date_enrolled.strftime('%Y-%m-%d'),
            enr.status.title()
        ])
        
    pdf = generate_pdf_report(data, title="University Enrollment Report")
    return send_file(pdf, as_attachment=True, download_name='enrollment_report.pdf', mimetype='application/pdf')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('admin.settings'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('admin.settings'))

        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/settings.html')

@admin_bp.route('/students/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'student':
        flash('Cannot edit non-student users here.', 'warning')
        return redirect(url_for('admin.manage_students'))
        
    details = StudentDetails.query.filter_by(user_id=user.id).first()
    if not details:
        # Create details if missing (should rarely happen for registered students)
        details = StudentDetails(user_id=user.id)
        db.session.add(details)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        details.phone = request.form.get('phone')
        details.dob = request.form.get('dob')
        
        try:
            db.session.commit()
            flash('Student details updated successfully.', 'success')
            return redirect(url_for('admin.manage_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')
            
    return render_template('admin/edit_student.html', user=user, details=details)

@admin_bp.route('/enrollments')
@admin_required
def enrollments():
    # Helper to avoid ambiguous join: start from Enrollment, join StudentDetails, then User, then Course
    all_enrollments = db.session.query(Enrollment, User, Course).select_from(Enrollment).join(StudentDetails).join(User).join(Course).all()
    return render_template('admin/enrollments.html', enrollments=all_enrollments)

    return render_template('admin/enrollments.html', enrollments=all_enrollments)
