from django.contrib import admin
from .models import Student, Course, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'gender', 'department', 'email', 'phone', 'date_joined')
    search_fields = ('student_id', 'full_name', 'department', 'email')
    list_filter = ('gender', 'department', 'date_joined')
    ordering = ('student_id',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'total_enrolled')
    search_fields = ('code', 'name', 'teacher')
    filter_horizontal = ('students',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status')
    list_filter = ('status', 'date', 'course')
    search_fields = ('student__full_name', 'student__student_id', 'course__name', 'course__code')
    date_hierarchy = 'date'
