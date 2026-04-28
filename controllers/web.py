from flask import Blueprint, request, render_template, redirect, url_for
import DB_manager_sql as db_manager


web_bp = Blueprint("web", __name__)


def html_call(template, controller, *args):
    try:
        result = controller(*args)
        if result is None:
            return render_template("error.html", code=404, message="not found"), 404
        return render_template(template, data=result), 200
    except TypeError as e:
        return render_template("error.html", code=400, error=str(e)), 400
    except NotImplementedError as e:
        return render_template("error.html", code=501, error=str(e)), 501


@web_bp.route("/")
def home():
    s_var = request.args.get("seniority_var", 0, type=float)
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")
    employees = db_manager.get_employees(min_seniority=s_var, sort_by=sort_by, order=order)
    return render_template(
        "employees_list.html",
        data=employees,
        seniority_var=s_var,
        sort_by=sort_by,
        order=order,
    )


@web_bp.route("/one_employee_list/<int:emp_id>", methods=["GET", "POST"])
def list_employee(emp_id):
    return html_call("one_employee_list.html", db_manager.get_employee, emp_id)


@web_bp.route("/employees_list/<int:emp_id>", methods=["GET", "POST"])
def erasing_employee(emp_id):
    db_manager.delete_employee(emp_id)
    return redirect(url_for("web.home"))


@web_bp.route("/add_employee", methods=["GET", "POST"])
def manage_add_employee():
    if request.method == "POST":
        emp = {
            "name": request.form["emp_name"],
            "department": request.form["emp_department"],
            "hire_date": request.form["emp_hire_date"],
            "salary": request.form["emp_salary"],
            "office_id": request.form["emp_office_id"],
        }
        db_manager.add_employee(emp)
        return redirect(url_for("web.home"))
    return render_template("add_employee.html")


@web_bp.route("/edit_employee/<int:edit_id>")
def edit_employee_page(edit_id):
    employee = db_manager.get_employee(edit_id)
    offices = db_manager.get_all_offices()
    if employee is None:
        return render_template("error.html", code=404, message="Employee not found"), 404
    return render_template("employee_edit.html", employee=employee, offices=offices)


@web_bp.route("/update_employee/<int:edit_id>", methods=["POST"])
def manage_update_employee(edit_id):
    o_id = request.form.get("emp_office_id")
    office_id = int(o_id) if o_id and o_id != "None" and o_id != "" else None

    emp = {
        "name": request.form["emp_name"],
        "department": request.form["emp_department"],
        "hire_date": request.form["emp_hire_date"],
        "salary": float(request.form["emp_salary"]),
        "office_id": office_id,
    }
    db_manager.update_employee(edit_id, emp)
    return redirect(url_for("web.home"))


@web_bp.route("/assign_employees", methods=["GET", "POST"])
def manage_assign_employees():
    if request.method == "POST":
        office_id = request.form.get("office_id")
        employee_ids = request.form.getlist("employee_ids")
        if office_id and employee_ids:
            db_manager.assign_employees_to_office(office_id, employee_ids)
        return redirect(url_for("web.list_offices"))

    offices = db_manager.get_all_offices()
    employees = db_manager.get_all_employees()
    return render_template("assign_employees.html", offices=offices, employees=employees)


@web_bp.route("/offices")
def list_offices():
    f_var = request.args.get("floor_var", 0, type=int)
    f_type = request.args.get("filter_type", "all")
    min_count = request.args.get("min_count", default=None, type=int)
    max_count = request.args.get("max_count", default=None, type=int)
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")

    data = db_manager.get_offices(
        floor=f_var,
        f_type=f_type,
        min_count=min_count,
        max_count=max_count,
        sort_by=sort_by,
        order=order,
    )
    return render_template(
        "office_list.html",
        data=data,
        floor_var=f_var,
        filter_type=f_type,
        min_count=min_count,
        max_count=max_count,
        sort_by=sort_by,
        order=order,
    )


@web_bp.route("/one_office_list/<int:office_id>", methods=["GET", "POST"])
def list_one_office(office_id):
    return html_call("one_office_list.html", db_manager.get_office, office_id)


@web_bp.route("/add_office", methods=["GET", "POST"])
def manage_add_office():
    if request.method == "POST":
        office = {
            "floor": request.form["office_floor"],
            "room_number": request.form["office_room_number"],
            "capacity": request.form["office_capacity"],
        }
        db_manager.add_office(office)
        return redirect(url_for("web.home"))
    return render_template("add_office.html")


@web_bp.route("/offices/<int:office_id>", methods=["GET", "POST"])
def erasing_office(office_id):
    db_manager.delete_office(office_id)
    return redirect(url_for("web.list_offices"))


@web_bp.route("/edit_office/<int:office_id>", methods=["GET", "POST"])
def edit_office_page(office_id):
    if request.method == "POST":
        office = {
            "floor": request.form["office_floor"],
            "room_number": request.form["office_room_number"],
            "capacity": request.form["office_capacity"],
        }
        db_manager.update_office(office_id, office)
        return redirect(url_for("web.list_offices"))

    office = db_manager.get_office(office_id)
    if office is None:
        return render_template("error.html", code=404, message="Office not found"), 404
    return render_template("edit_office.html", office=office)

