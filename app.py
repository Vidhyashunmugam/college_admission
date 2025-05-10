import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3

from models import db, Admin, Student
from forms import RegistrationForm, AdminLoginForm
from pdf_generator import generate_admission_pdf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college_admission.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PDF_FOLDER'] = 'pdfs'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/')
def index():
    form = RegistrationForm()
    current_year = datetime.now().year
    return render_template('index.html', form=form, current_year=current_year)

@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        existing_student = Student.query.filter_by(email=form.email.data).first()
        if existing_student:
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('index.html', form=form)
        
        # Create new student
        student = Student(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data,
            course=form.course.data,
            registration_date=datetime.now(),
            status='Pending'
        )
        
        db.session.add(student)
        db.session.commit()
        
        # Generate PDF
        pdf_filename = f"admission_{student.id}.pdf"
        pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
        generate_admission_pdf(student, pdf_path)
        
        flash('Registration successful! Your application is pending approval.', 'success')
        return redirect(url_for('download_pdf', filename=pdf_filename))
    
    return render_template('index.html', form=form)

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_from_directory(app.config['PDF_FOLDER'], filename, as_attachment=True)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    form = AdminLoginForm()
    current_year = datetime.now().year
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        
        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin_login.html', form=form, current_year=current_year)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Fetch all students from the database
    students = Student.query.all()
    current_year = datetime.now().year
    return render_template('admin_dashboard.html', students=students, current_year=current_year)

@app.route('/admin/approve/<int:student_id>')
@login_required
def approve_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = 'Approved'
    db.session.commit()
    flash(f'Student {student.full_name} has been approved', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:student_id>')
@login_required
def reject_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = 'Rejected'
    db.session.commit()
    flash(f'Student {student.full_name} has been rejected', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/remove/<int:student_id>')
@login_required
def remove_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {student.full_name} has been removed', 'info')
    return redirect(url_for('admin_dashboard'))

# Initialize the application and create an admin user if not exists
def init_app():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_app()  # Initialize admin user
    app.run(debug=True)
    