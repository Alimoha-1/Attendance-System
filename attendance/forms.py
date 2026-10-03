from django import forms
from .models import Student, Course, Attendance


class StudentForm(forms.ModelForm):
    """
    Form for adding and editing students.
    """
    class Meta:
        model = Student
        fields = ['student_id', 'full_name', 'gender', 'department', 'email', 'phone', 'date_joined']
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., STD-2024-001'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full legal name'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science, Grade 10-A'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@school.edu'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 000-0000'
            }),
            'date_joined': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class CourseForm(forms.ModelForm):
    """
    Form for adding and editing courses/classes.
    """
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text="Select students to enroll in this course (optional, you can also select all students)."
    )

    class Meta:
        model = Course
        fields = ['name', 'code', 'teacher', 'description', 'students']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Introduction to Computer Science'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CS101'
            }),
            'teacher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Prof. Sarah Jenkins'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief course overview and syllabus notes...'
            }),
        }
