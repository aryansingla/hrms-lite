import json
from datetime import date
from urllib.parse import urlencode

from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from django.contrib import messages

from .forms import EmployeeForm, AttendanceForm
from .models import Employee, Attendance


@require_GET
def dashboard(request: HttpRequest):
    total_employees = Employee.objects.count()
    total_attendance_today = Attendance.objects.filter(date=date.today()).count()
    present_today = Attendance.objects.filter(date=date.today(), status=Attendance.STATUS_PRESENT).count()

    top_present = (
        Employee.objects.annotate(
            present_days=Count("attendance_records", filter=Q(attendance_records__status=Attendance.STATUS_PRESENT))
        )
        .order_by("-present_days")[:5]
    )

    return render(
        request,
        "core/dashboard.html",
        {
            "total_employees": total_employees,
            "total_attendance_today": total_attendance_today,
            "present_today": present_today,
            "top_present": top_present,
        },
    )


def _employee_list_query_params(request):
    """Build query string for employee list filters (for pagination links)."""
    params = {}
    for key in ("name", "email", "department"):
        val = request.GET.get(key, "").strip()
        if val:
            params[key] = val
    return urlencode(params)


@require_http_methods(["GET", "POST"])
def employee_list(request: HttpRequest):
    base_qs = Employee.objects.annotate(
        present_days=Count(
            "attendance_records",
            filter=Q(attendance_records__status=Attendance.STATUS_PRESENT),
        )
    )

    filter_name = request.GET.get("name", "").strip()
    filter_email = request.GET.get("email", "").strip()
    filter_department = request.GET.get("department", "").strip()
    if filter_name:
        base_qs = base_qs.filter(full_name__icontains=filter_name)
    if filter_email:
        base_qs = base_qs.filter(email__icontains=filter_email)
    if filter_department:
        base_qs = base_qs.filter(department__icontains=filter_department)

    paginator = Paginator(base_qs.order_by("full_name"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    employees = page_obj.object_list
    form = EmployeeForm()

    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Employee added.")
                return redirect("employee_list")
            except Exception as exc:
                form.add_error(None, str(exc))

    query_params = _employee_list_query_params(request)

    return render(
        request,
        "core/employee_list.html",
        {
            "employees": employees,
            "form": form,
            "page_obj": page_obj,
            "filter_name": filter_name,
            "filter_email": filter_email,
            "filter_department": filter_department,
            "query_params": query_params,
        },
    )


@require_http_methods(["POST"])
def employee_create(request: HttpRequest):
    form = EmployeeForm(request.POST)
    if form.is_valid():
        try:
            form.save()
        except Exception as exc:
            messages.error(request, f"Could not create employee: {exc}")
    else:
        messages.error(request, "Please fix errors in the form.")
    return redirect("employee_list")


@require_http_methods(["POST"])
def employee_delete(request: HttpRequest, pk: int):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    messages.success(request, "Employee deleted.")
    return redirect("employee_list")


@require_http_methods(["GET", "POST"])
def attendance_mark(request: HttpRequest):
    form = AttendanceForm(initial={"date": date.today()})

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Attendance recorded.")
                return redirect("attendance_overview")
            except Exception as exc:
                form.add_error(None, str(exc))

    return render(request, "core/attendance_mark.html", {"form": form})


def _attendance_query_params(request, selected_date_str):
    """Build query string for attendance filters (for pagination links)."""
    params = {"date": selected_date_str}
    for key in ("name", "department", "status_filter"):
        val = request.GET.get(key, "").strip()
        if val:
            params[key] = val
    return urlencode(params)


@require_http_methods(["GET", "POST"])
def attendance_overview(request: HttpRequest):
    employees_qs = Employee.objects.annotate(
        present_days=Count(
            "attendance_records",
            filter=Q(attendance_records__status=Attendance.STATUS_PRESENT),
        )
    )

    filter_name = request.GET.get("name", "").strip()
    filter_department = request.GET.get("department", "").strip()
    filter_status = request.GET.get("status_filter", "").strip().lower()
    if filter_name:
        employees_qs = employees_qs.filter(full_name__icontains=filter_name)
    if filter_department:
        employees_qs = employees_qs.filter(department__icontains=filter_department)

    employees_qs = employees_qs.order_by("full_name")
    selected_date_str = request.GET.get("date") or request.POST.get("date")
    if not selected_date_str:
        selected_date = date.today()
        selected_date_str = selected_date.isoformat()
    else:
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except ValueError:
            messages.error(request, "Invalid date. Showing today instead.")
            selected_date = date.today()
            selected_date_str = selected_date.isoformat()

    if request.method == "POST":
        status = request.POST.get("status")
        selected_ids = request.POST.getlist("employee_ids")
        if not selected_ids:
            messages.error(request, "Select at least one employee.")
        elif status not in {Attendance.STATUS_PRESENT, Attendance.STATUS_ABSENT}:
            messages.error(request, "Choose a valid status.")
        else:
            for emp_id in selected_ids:
                try:
                    employee = Employee.objects.get(pk=emp_id)
                except Employee.DoesNotExist:
                    continue
                Attendance.objects.update_or_create(
                    employee=employee,
                    date=selected_date,
                    defaults={"status": status},
                )
            messages.success(request, "Attendance saved.")
            qp = [f"date={selected_date_str}"]
            if filter_name:
                qp.append(f"name={filter_name}")
            if filter_department:
                qp.append(f"department={filter_department}")
            if filter_status:
                qp.append(f"status_filter={filter_status}")
            return redirect(f"{request.path}?{'&'.join(qp)}")

    existing_records = {
        a.employee_id: a
        for a in Attendance.objects.filter(
            date=selected_date, employee__in=employees_qs
        ).select_related("employee")
    }

    employees_with_status = []
    for emp in employees_qs:
        record = existing_records.get(emp.id)
        emp.current_status = record.status if record else ""
        emp.current_status_label = record.get_status_display() if record else "Not marked"
        employees_with_status.append(emp)

    if filter_status == "present":
        employees_with_status = [e for e in employees_with_status if e.current_status == Attendance.STATUS_PRESENT]
    elif filter_status == "absent":
        employees_with_status = [e for e in employees_with_status if e.current_status == Attendance.STATUS_ABSENT]
    elif filter_status == "not_marked":
        employees_with_status = [e for e in employees_with_status if not e.current_status]

    paginator = Paginator(employees_with_status, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/attendance_overview.html",
        {
            "employees": page_obj.object_list,
            "page_obj": page_obj,
            "selected_date": selected_date_str,
            "filter_name": filter_name,
            "filter_department": filter_department,
            "filter_status": filter_status,
            "query_params": _attendance_query_params(request, selected_date_str),
        },
    )


@require_GET
def employee_attendance_detail(request: HttpRequest, pk: int):
    employee = get_object_or_404(Employee, pk=pk)
    qs = employee.attendance_records.order_by("-date")
    present_days = qs.filter(status=Attendance.STATUS_PRESENT).count()
    records = qs[:90]
    return render(
        request,
        "core/employee_attendance_detail.html",
        {"employee": employee, "records": records, "present_days": present_days},
    )


@require_http_methods(["GET", "POST"])
def api_employees(request: HttpRequest):
    if request.method == "GET":
        data = [
            {
                "id": e.id,
                "employee_id": e.employee_id,
                "full_name": e.full_name,
                "email": e.email,
                "department": e.department,
            }
            for e in Employee.objects.all()
        ]
        return JsonResponse(data, safe=False)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    form = EmployeeForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    try:
        employee = form.save()
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(
        {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "email": employee.email,
            "department": employee.department,
        },
        status=201,
    )


@require_http_methods(["GET", "POST"])
def api_attendance(request: HttpRequest):
    if request.method == "GET":
        employee_id = request.GET.get("employee_id")
        qs = Attendance.objects.select_related("employee").all()
        if employee_id:
            qs = qs.filter(employee__employee_id=employee_id)

        data = [
            {
                "employee_id": a.employee.employee_id,
                "full_name": a.employee.full_name,
                "date": a.date.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]
        return JsonResponse(data, safe=False)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    form = AttendanceForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    try:
        record = form.save()
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(
        {
            "employee_id": record.employee.employee_id,
            "full_name": record.employee.full_name,
            "date": record.date.isoformat(),
            "status": record.status,
        },
        status=201,
    )

