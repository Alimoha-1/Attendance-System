from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Authentication
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),

    # Student Management
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    # Course Management
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_create, name='course_create'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),

    # Attendance
    path('attendance/take/', views.take_attendance, name='take_attendance'),
    path('attendance/records/', views.attendance_records, name='attendance_records'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('attendance/export/', views.export_attendance_csv, name='export_attendance_csv'),

    # Reports
    path('reports/', views.student_report, name='student_report'),
    path('reports/export/', views.export_reports_csv, name='export_reports_csv'),
]
