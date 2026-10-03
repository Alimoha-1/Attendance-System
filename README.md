# Student Attendance Management System

A clean, modern, and production-ready **Student Attendance Management System** built with **Django (Python)**, **SQLite**, and **Bootstrap 5**.

---

## 🌟 Full Real-World Features

1. **Dashboard**
   - Live metrics directly calculated from the database
   - Today's attendance counters: Present, Absent, Late, and Presence Rate (%)
   - Recent activity stream with status badges
   - Quick action shortcuts

2. **Student Management**
   - Full CRUD (Register, View Profile, Edit, Delete)
   - Real-time search across Full Name, Student ID, Department, and Email
   - Individual **Student Profile Page** showing contact info, enrolled courses, and lifetime attendance history

3. **Course & Class Management**
   - Manage Course Name, Course Code, Instructor, and Description
   - Course Roster & Enrolled Students assignment
   - Individual **Course Overview Page** showing roster and class performance stats

4. **Take Attendance**
   - Select Course/Class and Session Date
   - Displays registered class roster
   - Quick batch controls: **All Present**, **All Absent**, **All Late**
   - **Duplicate Prevention:** Seamlessly updates existing attendance for the same student, course, and date without crashing

5. **Attendance Records**
   - Multi-criteria filter: Date, Student, Course, Status
   - Live summary counters (Total, Present, Absent, Late)
   - Single-record deletion tool for correcting teacher mistakes
   - **Export to CSV:** Download filtered logs directly to Excel/CSV
   - Print-friendly layout

6. **Student Attendance Reports**
   - Per-student performance table: Total classes, Present, Absent, Late
   - Automated percentage calculation with color-coded progress bars (Green ≥ 75%, Yellow 50–74%, Red < 50%)
   - Filter by course or student search
   - **Export to CSV** and **Print Report** buttons

7. **Authentication & Security**
   - Secure Django session authentication
   - All management pages protected from unauthenticated access
   - Built-in **Change Password** feature for the admin user

---

## 🚀 How to Run the Project

### 1. Activate Virtual Environment
```powershell
# Windows
venv\Scripts\activate
```

### 2. Install Dependencies (if not already installed)
```powershell
pip install -r requirements.txt
```

### 3. Run the Server
```powershell
python manage.py runserver
```

Open your browser and navigate to:
**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Administrator Login

- **Username:** `admin`
- **Password:** `admin123`

*(You can change your password anytime via the user menu in the top-right corner or create new superusers with `python manage.py createsuperuser`)*
