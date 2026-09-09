# Hospital_management_system
A web-based Hospital Management System developed using Django and Python. 
The system is designed to manage hospital activities such as patient registration, 
doctor management, appointments, billing, and role-based access.

## Features

- User Registration and Login
- Role-Based Access Control
- Patient Management
- Doctor Management
- Appointment Management
- Billing Management
- Patient Records
- Doctor Dashboard
- Hospital Staff Management
- Admin Dashboard
- Secure Authentication
- User-Friendly Interface
- Bootstrap-Based Responsive Design

## User Roles

### Admin
- Manage doctors
- Manage hospital staff
- Manage patients
- Manage appointments
- Manage billing
- View and manage overall hospital information

### Doctor
- Login to the system
- View assigned appointments
- View patient information
- Manage patient records
- Update medical information

### Hospital Staff
- Register patients
- Manage patient information
- Schedule appointments
- Manage billing information
- View required hospital records

### Patient
- Register and login
- View personal information
- View appointments
- View billing information
- View relevant medical records

## Technologies Used

- Python
- Django
- HTML5
- CSS3
- Bootstrap
- JavaScript
- SQLite
- Git & GitHub

## Project Structure

```text
Hospital_management/
│
├── manage.py
├── db.sqlite3
│
├── hospital/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── patient/
│   ├── doctor/
│   ├── appointment/
│   └── billing/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
