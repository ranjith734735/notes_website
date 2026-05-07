# College Notes Sharing Website

A modern web application for college students and faculty to share and access study notes using Flask and Python.

## Features

- ✅ Separate login for students and faculty
- ✅ Faculty can upload and delete notes
- ✅ Students can download notes
- ✅ Organize notes by Department (CSE, AI&DS, BME, AGRI, MECH) and Subject
- ✅ Search and filter functionality
- ✅ User profiles
- ✅ Modern, responsive UI
- ✅ Secure password hashing

## Installation

### 1. Prerequisites
- Python 3.7+
- pip (Python package manager)

### 2. Setup

Clone or navigate to the project directory:
```bash
cd "NOTES WEBSITE"
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Deployment

This project is ready for deployment. The following files are included:
- `Procfile` — tells the platform how to start the app using Gunicorn
- `runtime.txt` — specifies the Python version
- `requirements.txt` — packages needed for production
- `.gitignore` — excludes local database and uploads from version control

### Deploy on Render / Railway / Heroku-style host
1. Create a GitHub repository for this folder.
2. Push the code to GitHub.
3. Connect the repository to your hosting service.
4. Use `web: gunicorn app:app` as the start command.
5. Ensure the service uses Python 3.11 or later.

## Usage

### For Students:
1. Register with username, password, and select "Student" role
2. Login with your credentials
3. Browse notes by department and subject
4. Use search/filter to find specific notes
5. Download notes to your device

### For Faculty:
1. Register with username, password, and select "Faculty" role
2. Login with your credentials
3. Click "Upload Note" to add new study materials
4. Select department and subject
5. Upload the file (supports PDF, DOC, DOCX, TXT, PPT, PPTX)
6. Manage your uploaded notes - delete as needed
7. View your profile to see upload statistics

## File Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── dashboard.html   # Main dashboard
│   ├── upload.html      # Upload notes page
│   └── profile.html     # User profile
├── static/
│   └── style.css        # Styling
├── uploads/             # Uploaded notes storage
└── notes.db            # SQLite database

```

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing
- **Frontend**: HTML5, CSS3
- **File Handling**: Werkzeug

## Security Features

- Password hashing with Werkzeug security
- Session-based authentication
- CSRF protection
- File type validation
- File size limits (50MB max)
- Role-based access control

## Departments

- CSE (Computer Science Engineering)
- AI&DS (Artificial Intelligence & Data Science)
- BME (Biomedical Engineering)
- AGRI (Agricultural Engineering)
- MECH (Mechanical Engineering)

## Database

SQLite database (`notes.db`) is automatically created on first run.

**Users Table**: Stores username, hashed password, and role
**Notes Table**: Stores note metadata (title, file, department, subject, uploader, timestamp)

## Support

For issues or questions, check that:
- All dependencies are installed: `pip install -r requirements.txt`
- Python version is 3.7 or higher
- Port 5000 is available
- Uploads folder has write permissions