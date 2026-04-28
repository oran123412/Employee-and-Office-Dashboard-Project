from flask import Blueprint, request, jsonify
import DB_manager_sql as db


api_bp = Blueprint("api", __name__, url_prefix="/api")


def _ok(result, status=200):
    return jsonify({"success": True, "result": result}), status


def _err(message, status=400):
    return jsonify({"success": False, "error": message}), status


@api_bp.get("/offices")
def api_list_offices():
    floor = request.args.get("floor", 0, type=int)
    f_type = request.args.get("filter_type", "all")
    min_count = request.args.get("min_count", default=None, type=int)
    max_count = request.args.get("max_count", default=None, type=int)
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")
    return _ok(db.get_offices(floor=floor, f_type=f_type, min_count=min_count, max_count=max_count, sort_by=sort_by, order=order))


@api_bp.get("/offices/<int:office_id>")
def api_get_office(office_id: int):
    office = db.get_office(office_id)
    if office is None:
        return _err("office not found", 404)
    return _ok(office)


@api_bp.post("/offices")
def api_create_office():
    payload = request.get_json(silent=True) or {}
    try:
        office = {
            "floor": int(payload["floor"]),
            "room_number": str(payload["room_number"]),
            "capacity": int(payload["capacity"]),
        }
    except Exception:
        return _err("invalid payload. expected: floor, room_number, capacity", 400)
    db.add_office(office)
    return _ok({"created": True}, 201)


@api_bp.put("/offices/<int:office_id>")
@api_bp.patch("/offices/<int:office_id>")
def api_update_office(office_id: int):
    if db.get_office(office_id) is None:
        return _err("office not found", 404)
    payload = request.get_json(silent=True) or {}
    try:
        office = {
            "floor": int(payload["floor"]),
            "room_number": str(payload["room_number"]),
            "capacity": int(payload["capacity"]),
        }
    except Exception:
        return _err("invalid payload. expected: floor, room_number, capacity", 400)
    db.update_office(office_id, office)
    return _ok({"updated": True})


@api_bp.delete("/offices/<int:office_id>")
def api_delete_office(office_id: int):
    if db.get_office(office_id) is None:
        return _err("office not found", 404)
    db.delete_office(office_id)
    return _ok({"deleted": True})


@api_bp.get("/offices/<int:office_id>/employees")
def api_office_employees(office_id: int):
    office = db.get_office(office_id)
    if office is None:
        return _err("office not found", 404)
    return _ok(office.get("employees", []))


@api_bp.post("/offices/<int:office_id>/assign")
def api_assign_employees_to_office(office_id: int):
    if db.get_office(office_id) is None:
        return _err("office not found", 404)
    payload = request.get_json(silent=True) or {}
    employee_ids = payload.get("employee_ids")
    if not isinstance(employee_ids, list) or not employee_ids:
        return _err("invalid payload. expected: employee_ids: [int,...]", 400)
    try:
        employee_ids = [int(x) for x in employee_ids]
    except Exception:
        return _err("employee_ids must be integers", 400)
    db.assign_employees_to_office(office_id, employee_ids)
    return _ok({"assigned": len(employee_ids)})


@api_bp.get("/employees")
def api_list_employees():
    min_seniority = request.args.get("min_seniority", 0, type=float)
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")
    return _ok(db.get_employees(min_seniority=min_seniority, sort_by=sort_by, order=order))


@api_bp.get("/employees/<int:emp_id>")
def api_get_employee(emp_id: int):
    emp = db.get_employee(emp_id)
    if emp is None:
        return _err("employee not found", 404)
    return _ok(emp)


@api_bp.post("/employees")
def api_create_employee():
    payload = request.get_json(silent=True) or {}
    try:
        office_id = payload.get("office_id", None)
        office_id = int(office_id) if office_id is not None else None
        emp = {
            "name": str(payload["name"]),
            "department": str(payload["department"]),
            "salary": float(payload["salary"]),
            "hire_date": str(payload["hire_date"]),
            "office_id": office_id,
        }
    except Exception:
        return _err("invalid payload. expected: name, department, salary, hire_date, office_id(optional)", 400)
    db.add_employee(emp)
    return _ok({"created": True}, 201)


@api_bp.put("/employees/<int:emp_id>")
@api_bp.patch("/employees/<int:emp_id>")
def api_update_employee(emp_id: int):
    if db.get_employee(emp_id) is None:
        return _err("employee not found", 404)
    payload = request.get_json(silent=True) or {}
    try:
        office_id = payload.get("office_id", None)
        office_id = int(office_id) if office_id is not None else None
        emp = {
            "name": str(payload["name"]),
            "department": str(payload["department"]),
            "salary": float(payload["salary"]),
            "hire_date": str(payload["hire_date"]),
            "office_id": office_id,
        }
    except Exception:
        return _err("invalid payload. expected: name, department, salary, hire_date, office_id(optional)", 400)
    db.update_employee(emp_id, emp)
    return _ok({"updated": True})


@api_bp.delete("/employees/<int:emp_id>")
def api_delete_employee(emp_id: int):
    if db.get_employee(emp_id) is None:
        return _err("employee not found", 404)
    db.delete_employee(emp_id)
    return _ok({"deleted": True})

