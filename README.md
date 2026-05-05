# SecureShare

SecureShare is a secure file sharing web application developed with Django. The system allows users to upload, encrypt, download, and manage files securely while maintaining activity logs for better tracking and monitoring.

## Features

- User authentication system
- Secure file upload and storage
- File encryption for better security
- Download file management
- Activity logging (upload, download, delete)
- Email notification system for secure file sharing
- User dashboard
- Secure environment variable management
- Clean and user-friendly interface

## Technologies Used

- Python
- Django
- HTML
- CSS
- Bootstrap
- SQLite

## Project Structure

```text
SecureShare/
│── fileshare/
│── secureshare/
│── manage.py
│── README.md
│── .gitignore
```

## Security Configuration

Sensitive credentials and private keys are excluded from GitHub using `.gitignore`.

Ignored files:

```text
.env
private.pem
public.pem
db.sqlite3
media/
venv/
__pycache__/
```

Environment variables are used for email configuration:

```python
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
```

## Installation Guide

### 1. Clone the repository

```bash
git clone https://github.com/ArifaShorna/SecureShare.git
```

### 2. Move into project directory

```bash
cd SecureShare
```

### 3. Create virtual environment

```bash
python -m venv venv
```

### 4. Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install required packages

```bash
pip install -r requirements.txt
```

### 6. Create `.env` file

Add:

```env
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

### 7. Apply migrations

```bash
python manage.py migrate
```

### 8. Run development server

```bash
python manage.py runserver
```

## Usage

- Register/Login
- Upload files securely
- Download files
- Track user activities
- Delete files safely
- Share files securely
- Receive email notifications for file sharing

  

## Future Improvements

- File sharing via secure links
- Expiry-based file access
- Cloud storage integration


## Author

**Arifa Akter Shorna**
(Institute of Information Technology, Jahangirnagar University)
