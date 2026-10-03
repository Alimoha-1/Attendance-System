import csv
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse

from .models import Student, Course, Attendance
from .forms import StudentForm, CourseForm


# ==============================================================================
# 1. Authentication Views
# ==============================================================================

def user_login(request):
    """
    Handle user login. Redirects already authenticated users to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'attendance/login.html', {'form': form})


def user_logout(request):
    """
    Handle user logout and redirect to login page with a farewell message.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required(login_url='login')
def change_password(request):
    """
    Allow authenticated admin users to change their account password.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Your password was successfully updated!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'attendance/change_password.html', {'form': form})


# ==============================================================================
# 2. Dashboard View
# ==============================================================================

@login_required(login_url='login')
def dashboard(request):
    """
    Main system dashboard displaying real database metrics, today's attendance stats,
    and recent activity.
    """
    today = timezone.localdate()

    # Total counts from database
    total_students = Student.objects.count()
    total_courses = Course.objects.count()

    # Today's attendance counts
    today_records = Attendance.objects.filter(date=today)
    today_attendance_count = today_records.count()
    today_present = today_records.filter(status='Present').count()
    today_absent = today_records.filter(status='Absent').count()
    today_late = today_records.filter(status='Late').count()

    # Calculate overall attendance percentage for today
    today_percentage = 0
    if today_attendance_count > 0:
        today_percentage = round((today_present / today_attendance_count) * 100, 1)

    # Recent attendance records
    recent_attendance = Attendance.objects.select_related('student', 'course').order_by('-date', '-id')[:8]

    # Quick list of courses
    courses = Course.objects.all()[:6]

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'today': today,
        'today_attendance_count': today_attendance_count,
        'today_present': today_present,
        'today_absent': today_absent,
        'today_late': today_late,
        'today_percentage': today_percentage,
        'recent_attendance': recent_attendance,
        'courses': courses,
    }
    return render(request, 'attendance/dashboard.html', context)


# ==============================================================================
# 3. Student Management Views
# ==============================================================================

@login_required(login_url='login')
def student_list(request):
    """
    List all students with search and filtering by query.
    """
    query = request.GET.get('q', '').strip()
    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(department__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'students': students,
        'query': query,
        'total_count': students.count()
    }
    return render(request, 'attendance/student_list.html', context)


@login_required(login_url='login')
def student_detail(request, pk):
    """
    View complete profile for a single student including course enrollments
    and full attendance history.
    """
    student = get_object_or_404(Student, pk=pk)
    attendances = Attendance.objects.filter(student=student).select_related('course').order_by('-date')

    total_classes = attendances.count()
    present_count = attendances.filter(status='Present').count()
    absent_count = attendances.filter(status='Absent').count()
    late_count = attendances.filter(status='Late').count()
    attendance_rate = round((present_count / total_classes * 100), 1) if total_classes > 0 else 0.0

    enrolled_courses = student.courses.all()

    context = {
        'student': student,
        'attendances': attendances,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_rate': attendance_rate,
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'attendance/student_detail.html', context)


@login_required(login_url='login')
def student_create(request):
    """
    Create a new student record.
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.full_name}' was added successfully.")
            return redirect('student_list')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = StudentForm()

    context = {
        'form': form,
        'title': 'Add New Student',
        'button_text': 'Save Student',
    }
    return render(request, 'attendance/student_form.html', context)


@login_required(login_url='login')
def student_edit(request, pk):
    """
    Edit an existing student record.
    """
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{student.full_name}' was updated successfully.")
            return redirect('student_list')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = StudentForm(instance=student)

    context = {
        'form': form,
        'student': student,
        'title': f'Edit Student: {student.full_name}',
        'button_text': 'Update Student',
    }
    return render(request, 'attendance/student_form.html', context)


@login_required(login_url='login')
def student_delete(request, pk):
    """
    Delete a student record with confirmation.
    """
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.success(request, f"Student '{name}' has been deleted.")
        return redirect('student_list')

    return render(request, 'attendance/student_confirm_delete.html', {'student': student})


# ==============================================================================
# 4. Course / Class Management Views
# ==============================================================================

@login_required(login_url='login')
def course_list(request):
    """
    List all courses with search capabilities.
    """
    query = request.GET.get('q', '').strip()
    courses = Course.objects.all().prefetch_related('students')

    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(teacher__icontains=query)
        )

    context = {
        'courses': courses,
        'query': query,
        'total_count': courses.count()
    }
    return render(request, 'attendance/course_list.html', context)


@login_required(login_url='login')
def course_detail(request, pk):
    """
    View course details, roster of enrolled students, and course-specific statistics.
    """
    course = get_object_or_404(Course, pk=pk)
    enrolled_students = course.students.all()
    course_attendances = Attendance.objects.filter(course=course).select_related('student').order_by('-date')[:15]

    total_records = Attendance.objects.filter(course=course).count()
    total_present = Attendance.objects.filter(course=course, status='Present').count()
    avg_rate = round((total_present / total_records * 100), 1) if total_records > 0 else 0.0

    context = {
        'course': course,
        'enrolled_students': enrolled_students,
        'course_attendances': course_attendances,
        'total_records': total_records,
        'avg_rate': avg_rate,
    }
    return render(request, 'attendance/course_detail.html', context)


@login_required(login_url='login')
def course_create(request):
    """
    Create a new course/class.
    """
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.name} ({course.code})' created successfully.")
            return redirect('course_list')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = CourseForm()

    context = {
        'form': form,
        'title': 'Add New Course / Class',
        'button_text': 'Create Course',
    }
    return render(request, 'attendance/course_form.html', context)


@login_required(login_url='login')
def course_edit(request, pk):
    """
    Edit an existing course.
    """
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.name}' updated successfully.")
            return redirect('course_list')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = CourseForm(instance=course)

    context = {
        'form': form,
        'course': course,
        'title': f'Edit Course: {course.name}',
        'button_text': 'Update Course',
    }
    return render(request, 'attendance/course_form.html', context)


@login_required(login_url='login')
def course_delete(request, pk):
    """
    Delete a course with confirmation.
    """
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        name = course.name
        course.delete()
        messages.success(request, f"Course '{name}' has been deleted.")
        return redirect('course_list')

    return render(request, 'attendance/course_confirm_delete.html', {'course': course})


# ==============================================================================
# 5. Take Attendance View
# ==============================================================================

@login_required(login_url='login')
def take_attendance(request):
    """
    Interface to select a course and date, display registered students,
    and mark each as Present, Absent, or Late.
    Prevents duplicate entries using update_or_create.
    """
    courses = Course.objects.all()
    selected_course_id = request.GET.get('course') or request.POST.get('course')
    selected_date_str = request.GET.get('date') or request.POST.get('date')

    if not selected_date_str:
        selected_date_str = timezone.localdate().strftime('%Y-%m-%d')

    selected_course = None
    students_with_status = []

    if selected_course_id:
        try:
            selected_course = Course.objects.get(id=selected_course_id)
        except Course.DoesNotExist:
            selected_course = None

    if selected_course:
        # Determine students to display:
        # If the course has enrolled students, show those; otherwise fall back to all students
        if selected_course.students.exists():
            enrolled_students = selected_course.students.all()
        else:
            enrolled_students = Student.objects.all()

        # Handle submission of attendance
        if request.method == 'POST' and 'save_attendance' in request.POST:
            try:
                attendance_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                attendance_date = timezone.localdate()

            saved_count = 0
            for student in enrolled_students:
                status_key = f'status_{student.id}'
                status_val = request.POST.get(status_key, 'Present')

                if status_val in ['Present', 'Absent', 'Late']:
                    # update_or_create prevents duplicate records for same student, course, and date
                    Attendance.objects.update_or_create(
                        student=student,
                        course=selected_course,
                        date=attendance_date,
                        defaults={'status': status_val}
                    )
                    saved_count += 1

            messages.success(
                request,
                f"Attendance successfully recorded for {saved_count} student(s) in "
                f"'{selected_course.name}' on {selected_date_str}."
            )
            return redirect(f"{request.path}?course={selected_course.id}&date={selected_date_str}")

        # For GET request (or after saving): Fetch existing attendance statuses for this date
        try:
            attendance_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            attendance_date = timezone.localdate()

        existing_records = Attendance.objects.filter(
            course=selected_course,
            date=attendance_date
        )
        existing_status_map = {rec.student_id: rec.status for rec in existing_records}

        for student in enrolled_students:
            current_status = existing_status_map.get(student.id, 'Present')
            students_with_status.append({
                'student': student,
                'status': current_status,
                'already_recorded': student.id in existing_status_map
            })

    context = {
        'courses': courses,
        'selected_course': selected_course,
        'selected_date': selected_date_str,
        'students_with_status': students_with_status,
    }
    return render(request, 'attendance/take_attendance.html', context)


# ==============================================================================
# 6. Attendance Records View & Delete & CSV Export
# ==============================================================================

@login_required(login_url='login')
def attendance_records(request):
    """
    Search and filter past attendance records with multiple criteria:
    Date, Student, Course, and Status.
    """
    records = Attendance.objects.select_related('student', 'course').all()

    # Filter parameters
    date_filter = request.GET.get('date', '').strip()
    student_filter = request.GET.get('student', '').strip()
    course_filter = request.GET.get('course', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if date_filter:
        records = records.filter(date=date_filter)

    if student_filter:
        records = records.filter(student_id=student_filter)

    if course_filter:
        records = records.filter(course_id=course_filter)

    if status_filter:
        records = records.filter(status=status_filter)

    # Summary statistics for the filtered records
    total_count = records.count()
    present_count = records.filter(status='Present').count()
    absent_count = records.filter(status='Absent').count()
    late_count = records.filter(status='Late').count()

    context = {
        'records': records,
        'students': Student.objects.all(),
        'courses': Course.objects.all(),
        'selected_date': date_filter,
        'selected_student': student_filter,
        'selected_course': course_filter,
        'selected_status': status_filter,
        'total_count': total_count,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
    }
    return render(request, 'attendance/attendance_records.html', context)


@login_required(login_url='login')
def attendance_delete(request, pk):
    """
    Delete a single attendance entry (in case of mistakes).
    """
    record = get_object_or_404(Attendance, pk=pk)
    student_name = record.student.full_name
    record_date = record.date
    record.delete()
    messages.success(request, f"Attendance record for {student_name} on {record_date} was deleted.")
    return redirect('attendance_records')


@login_required(login_url='login')
def export_attendance_csv(request):
    """
    Export filtered attendance records to an Excel-compatible CSV file.
    """
    records = Attendance.objects.select_related('student', 'course').all()

    date_filter = request.GET.get('date', '').strip()
    student_filter = request.GET.get('student', '').strip()
    course_filter = request.GET.get('course', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if date_filter: records = records.filter(date=date_filter)
    if student_filter: records = records.filter(student_id=student_filter)
    if course_filter: records = records.filter(course_id=course_filter)
    if status_filter: records = records.filter(status=status_filter)

    response = HttpResponse(content_type='text/csv')
    filename = f"attendance_records_{timezone.localdate().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Student ID', 'Student Name', 'Department', 'Course Code', 'Course Name', 'Teacher', 'Status'])

    for rec in records:
        writer.writerow([
            rec.date.strftime('%Y-%m-%d'),
            rec.student.student_id,
            rec.student.full_name,
            rec.student.department,
            rec.course.code,
            rec.course.name,
            rec.course.teacher,
            rec.status
        ])

    return response


# ==============================================================================
# 7. Student Attendance Report View & CSV Export
# ==============================================================================

@login_required(login_url='login')
def student_report(request):
    """
    Generates a comprehensive attendance report for each student,
    including total classes, present, absent, late, and calculated percentage.
    Can be filtered by course or student search.
    """
    course_id = request.GET.get('course', '').strip()
    query = request.GET.get('q', '').strip()

    students = Student.objects.all()
    courses = Course.objects.all()

    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(department__icontains=query)
        )

    selected_course = None
    if course_id:
        try:
            selected_course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            selected_course = None

    reports = []
    for student in students:
        student_attendances = Attendance.objects.filter(student=student)

        if selected_course:
            student_attendances = student_attendances.filter(course=selected_course)

        total_classes = student_attendances.count()
        present = student_attendances.filter(status='Present').count()
        absent = student_attendances.filter(status='Absent').count()
        late = student_attendances.filter(status='Late').count()

        if total_classes > 0:
            percentage = round((present / total_classes) * 100, 1)
        else:
            percentage = 0.0

        reports.append({
            'student': student,
            'total_classes': total_classes,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': percentage,
        })

    context = {
        'reports': reports,
        'courses': courses,
        'selected_course': selected_course,
        'query': query,
    }
    return render(request, 'attendance/student_report.html', context)


@login_required(login_url='login')
def export_reports_csv(request):
    """
    Export student attendance summary performance report to CSV.
    """
    course_id = request.GET.get('course', '').strip()
    query = request.GET.get('q', '').strip()

    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(department__icontains=query)
        )

    selected_course = Course.objects.filter(id=course_id).first() if course_id else None

    response = HttpResponse(content_type='text/csv')
    filename = f"student_attendance_summary_{timezone.localdate().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    course_label = f"{selected_course.name} ({selected_course.code})" if selected_course else "All Courses Combined"
    writer.writerow(['Student ID', 'Full Name', 'Department', 'Course Scope', 'Total Classes', 'Present', 'Absent', 'Late', 'Attendance Rate (%)'])

    for student in students:
        qs = Attendance.objects.filter(student=student)
        if selected_course:
            qs = qs.filter(course=selected_course)

        total = qs.count()
        present = qs.filter(status='Present').count()
        absent = qs.filter(status='Absent').count()
        late = qs.filter(status='Late').count()
        rate = round((present / total * 100), 1) if total > 0 else 0.0

        writer.writerow([
            student.student_id,
            student.full_name,
            student.department,
            course_label,
            total,
            present,
            absent,
            late,
            f"{rate}%"
        ])

    return response
