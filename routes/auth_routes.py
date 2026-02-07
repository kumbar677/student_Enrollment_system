from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, StudentDetails
from werkzeug.security import check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'warning')
            return redirect(url_for('auth.register'))

        # Create new user
        new_user = User(name=name, email=email, role='student')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush() # Flush to get ID for student details

        # Create student details linked to user with auto-generated enrollment number
        # Format: UNIV + Year + 3-digit-user-id
        from datetime import datetime
        current_year = datetime.now().year
        enroll_no = f"UNIV{current_year}{new_user.id:03d}"
        
        student_details = StudentDetails(user_id=new_user.id, enrollment_no=enroll_no)
        db.session.add(student_details)
        
        db.session.commit()
        
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            import random
            from datetime import timedelta
            
            # Generate 6-digit numeric OTP
            otp = f"{random.randint(100000, 999999)}"
            user.reset_otp = otp
            user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            
            # Also generate secure token for the link (optional, but good for one-click)
            # OR just link to manual reset page with OTP pre-filled? No, users like links.
            # But the user specifically complained about "manual token send a number".
            # Let's send the link AND the OTP number.
            
            # Create a link that auto-fills the OTP on the manual reset page
            reset_link = f"http://{request.host}{url_for('auth.manual_reset', otp=otp)}"
            
            print(f"\n[DEBUG] Verification OTP: {otp}\n[DEBUG] Link: {reset_link}\n")
            
            from flask import current_app
            from flask_mail import Message
            
            msg = Message('Password Reset Code',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[user.email])
            
            msg.body = f'''Your Password Reset Code is: {otp}

Enter this code on the password reset page, or click this link:
{reset_link}

This code expires in 15 minutes.
'''
            msg.html = f'''
            <div style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                <h2>Password Reset Request</h2>
                <p>Your Verification Code is:</p>
                <div style="font-size: 2em; letter-spacing: 5px; font-weight: bold; background: #f3f4f6; padding: 10px; margin: 20px 0;">{otp}</div>
                <p>Enter this code manually, or click the button below:</p>
                <a href="{reset_link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
                <p style="margin-top: 20px; color: #6b7280; font-size: 0.9em;">If you did not request this, please ignore this email.</p>
            </div>
            '''
            
            mail = current_app.extensions['mail']
            try:
                mail.send(msg)
                flash('Check your email for the 6-digit verification code.', 'info')
                return redirect(url_for('auth.manual_reset')) # Send them to enter code page
            except Exception as e:
                flash(f'Error sending email: {e}', 'danger')
                
        else:
            flash('Email address not found.', 'danger')
             
        return redirect(url_for('auth.manual_reset'))
        
    return render_template('auth/forgot_password.html')

@auth_bp.route('/manual-reset', methods=['GET', 'POST'])
def manual_reset():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
        
    otp_from_url = request.args.get('otp')
    
    if request.method == 'POST':
        otp = request.form.get('token')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # If password fields are present, this is a PASSWORD CHANGE request
        if password and confirm_password:
             # We need to find the user by OTP again to be secure
             # (In a real app, use a hidden field or session, but querying by OTP is fair if OTP is unique enough for small time window)
             # Better: Use a hidden email field or session.
             # Simplest for this context: Ask user to re-enter OTP or keep it hidden.
             # I'll rely on the form submitting the OTP again as a hidden field or just reading it from 'token' input if it's there.
             pass
        
        # First verify OTP
        user = User.query.filter_by(reset_otp=otp).first()
        
        if not user:
            flash("Invalid Code.", "danger")
            return render_template('auth/manual_reset.html', otp=otp)
            
        if user.reset_otp_expiry < datetime.utcnow():
            flash("Code expired. Please request a new one.", "warning")
            return redirect(url_for('auth.forgot_password'))
            
        # If only OTP provided (Validation step) -> Show password fields
        if not password:
            return render_template('auth/manual_reset.html', otp=otp, valid_user=True)
            
        # If OTP + Password provided -> Update Password
        if password != confirm_password:
             flash("Passwords do not match.", "danger")
             return render_template('auth/manual_reset.html', otp=otp, valid_user=True)
             
        user.set_password(password)
        user.reset_otp = None # Clear OTP
        user.reset_otp_expiry = None
        db.session.commit()
        
        flash("Password updated successfully! Please login.", "success")
        return redirect(url_for('auth.login'))
            
    return render_template('auth/manual_reset.html', otp=otp_from_url)

# Legacy route redirect (optional)
@auth_bp.route('/reset-password/<token>')
def reset_password(token):
    return redirect(url_for('auth.manual_reset'))
