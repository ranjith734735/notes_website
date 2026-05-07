from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx'}
DEPARTMENTS = ['CSE', 'AI&DS', 'BME', 'AGRI', 'MECH']

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'faculty'
    notes = db.relationship('Note', backref='uploader', lazy=True, foreign_keys='Note.uploaded_by')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not all([username, password, role]):
            flash('All fields required', 'danger')
            return redirect(url_for('register'))

        if role not in ['student', 'faculty']:
            flash('Invalid role', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    subject = request.args.get('subject', '')

    query = Note.query
    if search:
        query = query.filter(Note.title.ilike(f'%{search}%') | Note.subject.ilike(f'%{search}%'))
    if department:
        query = query.filter_by(department=department)
    if subject:
        query = query.filter_by(subject=subject)

    notes = query.order_by(Note.department, Note.subject, Note.uploaded_at.desc()).all()

    # Group notes by department and subject
    grouped_notes = {}
    for note in notes:
        if note.department not in grouped_notes:
            grouped_notes[note.department] = {}
        if note.subject not in grouped_notes[note.department]:
            grouped_notes[note.department][note.subject] = []
        grouped_notes[note.department][note.subject].append(note)

    return render_template('dashboard.html', grouped_notes=grouped_notes, departments=DEPARTMENTS,
                         search=search, department=department, subject=subject)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'faculty':
        flash('Only faculty can upload notes', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)

        file = request.files['file']
        title = request.form.get('title')
        department = request.form.get('department')
        subject = request.form.get('subject')

        if not all([title, department, subject]):
            flash('All fields required', 'danger')
            return redirect(request.url)

        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filename = f"{datetime.now().timestamp()}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        note = Note(title=title, filename=filename, department=department,
                   subject=subject, uploaded_by=current_user.id)
        db.session.add(note)
        db.session.commit()
        flash('Note uploaded successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('upload.html', departments=DEPARTMENTS)

@app.route('/download/<int:note_id>')
@login_required
def download(note_id):
    if current_user.role != 'student':
        flash('Only students can download notes', 'danger')
        return redirect(url_for('dashboard'))

    note = Note.query.get_or_404(note_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
    return send_file(filepath, as_attachment=True, download_name=note.title)

@app.route('/delete/<int:note_id>', methods=['POST'])
@login_required
def delete(note_id):
    if current_user.role != 'faculty':
        flash('Only faculty can delete notes', 'danger')
        return redirect(url_for('dashboard'))

    note = Note.query.get_or_404(note_id)
    if note.uploaded_by != current_user.id:
        flash('You can only delete your own notes', 'danger')
        return redirect(url_for('dashboard'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    if current_user.role == 'faculty':
        uploaded_count = Note.query.filter_by(uploaded_by=current_user.id).count()
        return render_template('profile.html', uploaded_count=uploaded_count)
    return render_template('profile.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)