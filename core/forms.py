from django import forms

from .models import Employee, Attendance


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["employee_id", "full_name", "email", "department"]


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["employee", "date", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

