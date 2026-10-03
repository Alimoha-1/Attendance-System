from django.db import models
from django.utils import timezone


class Student(models.Model):
    """
    Model representing a student in the attendance system.
    """
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    student_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Student ID",
        help_text="Unique student registration number or ID"
    )
    full_name = models.CharField(
        max_length=120,
        verbose_name="Full Name"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='Male',
        verbose_name="Gender"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email Address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Phone Number"
    )
    department = models.CharField(
        max_length=100,
        verbose_name="Department / Class",
        help_text="e.g., Computer Science, Grade 10-A"
    )
    date_joined = models.DateField(
        default=timezone.now,
        verbose_name="Date Joined"
    )

    class Meta:
        ordering = ['student_id']
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


class Course(models.Model):
    """
    Model representing a course or class.
    """
    name = models.CharField(
        max_length=120,
        verbose_name="Course/Class Name"
    )
    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Course Code",
        help_text="e.g., CS101, MATH201"
    )
    teacher = models.CharField(
        max_length=120,
        verbose_name="Teacher / Lecturer"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    students = models.ManyToManyField(
        Student,
        blank=True,
        related_name="courses",
        verbose_name="Enrolled Students",
        help_text="Select students enrolled in this course (optional)"
    )

    class Meta:
        ordering = ['code']
        verbose_name = "Course / Class"
        verbose_name_plural = "Courses / Classes"

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_enrolled(self):
        return self.students.count()


class Attendance(models.Model):
    """
    Model representing daily attendance records for students per course.
    """
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Student"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Course / Class"
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="Date"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Present',
        verbose_name="Status"
    )

    class Meta:
        # Prevent duplicate attendance for the same student, course, and date
        unique_together = ('student', 'course', 'date')
        ordering = ['-date', 'course__code', 'student__full_name']
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.student.full_name} | {self.course.code} | {self.date} | {self.status}"
