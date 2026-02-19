from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("attendance/", views.attendance_overview, name="attendance_overview"),
    path("attendance/add/", views.attendance_mark, name="attendance_mark"),
    path("attendance/<int:pk>/employee/", views.employee_attendance_detail, name="employee_attendance_detail"),
    # Simple JSON APIs
    path("api/employees/", views.api_employees, name="api_employees"),
    path("api/attendance/", views.api_attendance, name="api_attendance"),
]

