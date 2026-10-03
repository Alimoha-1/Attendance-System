from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Student, Course, Attendance


class StudentAttendanceSystemTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testadmin', password='testpassword123')
        self.client = Client()

        # Create test student
        self.student = Student.objects.create(
            student_id='STD-TEST-001',
            full_name='Alice Test',
            gender='Female',
            department='Computer Science',
            email='alice@test.edu',
            phone='1234567890'
        )

        # Create test course
        self.course = Course.objects.create(
            name='Test Course',
            code='TC101',
            teacher='Dr. Turing',
            description='Test Description'
        )
        self.course.students.add(self.student)

    def test_unauthenticated_redirect(self):
        """Dashboard and management views must redirect to login if not logged in."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_login_and_dashboard(self):
        """Authenticated user should access dashboard successfully."""
        self.client.login(username='testadmin', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Overview')

    def test_student_crud_and_detail(self):
        """Test adding, viewing profile, editing, and deleting a student."""
        self.client.login(username='testadmin', password='testpassword123')

        # Add student
        create_response = self.client.post(reverse('student_create'), {
            'student_id': 'STD-TEST-002',
            'full_name': 'Bob Test',
            'gender': 'Male',
            'department': 'Physics',
            'email': 'bob@test.edu',
            'phone': '9876543210',
            'date_joined': '2024-01-15'
        })
        self.assertEqual(create_response.status_code, 302)
        self.assertTrue(Student.objects.filter(student_id='STD-TEST-002').exists())

        new_student = Student.objects.get(student_id='STD-TEST-002')

        # View student detail
        detail_response = self.client.get(reverse('student_detail', args=[new_student.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Bob Test')

        # Edit student
        edit_response = self.client.post(reverse('student_edit', args=[new_student.pk]), {
            'student_id': 'STD-TEST-002',
            'full_name': 'Bob Updated',
            'gender': 'Male',
            'department': 'Mathematics',
            'email': 'bob.new@test.edu',
            'phone': '9876543210',
            'date_joined': '2024-01-15'
        })
        self.assertEqual(edit_response.status_code, 302)
        new_student.refresh_from_db()
        self.assertEqual(new_student.full_name, 'Bob Updated')

        # Delete student
        delete_response = self.client.post(reverse('student_delete', args=[new_student.pk]))
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Student.objects.filter(student_id='STD-TEST-002').exists())

    def test_course_crud_and_detail(self):
        """Test adding, viewing details, editing, and deleting a course."""
        self.client.login(username='testadmin', password='testpassword123')

        # Add course
        response = self.client.post(reverse('course_create'), {
            'name': 'New Course',
            'code': 'NC202',
            'teacher': 'Dr. Newton',
            'description': 'Physics & Math',
            'students': [self.student.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(code='NC202').exists())

        course = Course.objects.get(code='NC202')

        # View course detail
        c_detail_response = self.client.get(reverse('course_detail', args=[course.pk]))
        self.assertEqual(c_detail_response.status_code, 200)
        self.assertContains(c_detail_response, 'New Course')

        # Edit course
        edit_response = self.client.post(reverse('course_edit', args=[course.pk]), {
            'name': 'Advanced Course',
            'code': 'NC202',
            'teacher': 'Dr. Newton',
            'description': 'Updated description',
            'students': [self.student.id]
        })
        self.assertEqual(edit_response.status_code, 302)
        course.refresh_from_db()
        self.assertEqual(course.name, 'Advanced Course')

        # Delete course
        del_response = self.client.post(reverse('course_delete', args=[course.pk]))
        self.assertEqual(del_response.status_code, 302)
        self.assertFalse(Course.objects.filter(code='NC202').exists())

    def test_take_attendance_and_prevent_duplicate(self):
        """Test recording attendance and updating existing attendance without duplicate records."""
        self.client.login(username='testadmin', password='testpassword123')
        today = timezone.localdate().strftime('%Y-%m-%d')

        save_response = self.client.post(reverse('take_attendance'), {
            'save_attendance': '1',
            'course': self.course.id,
            'date': today,
            f'status_{self.student.id}': 'Present'
        })
        self.assertEqual(save_response.status_code, 302)

        records = Attendance.objects.filter(student=self.student, course=self.course, date=today)
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first().status, 'Present')

        # Resubmit with Late
        update_response = self.client.post(reverse('take_attendance'), {
            'save_attendance': '1',
            'course': self.course.id,
            'date': today,
            f'status_{self.student.id}': 'Late'
        })
        self.assertEqual(update_response.status_code, 302)

        records_after = Attendance.objects.filter(student=self.student, course=self.course, date=today)
        self.assertEqual(records_after.count(), 1)
        self.assertEqual(records_after.first().status, 'Late')

    def test_attendance_records_delete_and_csv_export(self):
        """Test records filter, deletion of single record, and CSV exports."""
        self.client.login(username='testadmin', password='testpassword123')
        today = timezone.localdate()
        rec = Attendance.objects.create(student=self.student, course=self.course, date=today, status='Present')

        # Records view
        rec_response = self.client.get(reverse('attendance_records'))
        self.assertEqual(rec_response.status_code, 200)
        self.assertContains(rec_response, 'Alice Test')

        # CSV Export Attendance
        csv_resp = self.client.get(reverse('export_attendance_csv'))
        self.assertEqual(csv_resp.status_code, 200)
        self.assertEqual(csv_resp['Content-Type'], 'text/csv')
        self.assertIn(b'Alice Test', csv_resp.content)

        # CSV Export Reports
        rep_csv = self.client.get(reverse('export_reports_csv'))
        self.assertEqual(rep_csv.status_code, 200)
        self.assertEqual(rep_csv['Content-Type'], 'text/csv')
        self.assertIn(b'Alice Test', rep_csv.content)

        # Delete single attendance record
        del_resp = self.client.get(reverse('attendance_delete', args=[rec.pk]))
        self.assertEqual(del_resp.status_code, 302)
        self.assertFalse(Attendance.objects.filter(pk=rec.pk).exists())
