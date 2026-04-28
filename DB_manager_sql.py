import sqlite3

DB_FILE = 'company.db'


def query(sql, params=(), is_select=True):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        cursor.execute(sql, params)
        if is_select:
            return [dict(row) for row in cursor.fetchall()]
        conn.commit()

def create_tables():
    query('''CREATE TABLE IF NOT EXISTS offices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                floor INTEGER,
                room_number TEXT,
                capacity INTEGER)''', is_select=False)
    
    query('''CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                department TEXT,
                salary REAL,
                hire_date DATE,
                office_id INTEGER,
                FOREIGN KEY (office_id) REFERENCES offices(id))''', is_select=False)

def get_all_employees():
    return query("SELECT * FROM employees")

def get_employees(min_seniority=0, sort_by="id", order="asc"):
    sort_map = {
        "id": "employees.id",
        "name": "employees.name",
        "department": "employees.department",
        "hire_date": "employees.hire_date",
        "salary": "employees.salary",
        "seniority": "seniority",
        "office_id": "employees.office_id",
        "floor": "offices.floor",
        "room_number": "offices.room_number",
    }
    sort_col = sort_map.get(sort_by, "employees.id")
    order_sql = "DESC" if str(order).lower() == "desc" else "ASC"

    sql = f"""
        SELECT
            employees.*,
            offices.floor,
            offices.room_number,
            ROUND((julianday('now')-julianday(hire_date))/365.25, 1) AS seniority
        FROM employees
        LEFT JOIN offices ON employees.office_id = offices.id
        WHERE ROUND((julianday('now')-julianday(hire_date))/365.25, 1) >= ?
        ORDER BY {sort_col} {order_sql}
    """
    return query(sql, (min_seniority,))

def get_employees_with_seniority(min_seniority):
    return get_employees(min_seniority=min_seniority)


def add_employee(emp):
    sql = "INSERT INTO employees (name, department, salary, hire_date, office_id) VALUES (?, ?, ?, ?, ?)"
    params = (emp['name'], emp['department'], emp['salary'], emp['hire_date'], emp['office_id'])
    query(sql, params, is_select=False)

def delete_employee(emp_id):
    query("DELETE FROM employees WHERE id = ?", (emp_id,), is_select=False)

def get_employee(emp_id):
    res = query("SELECT *, ROUND((julianday('now') - julianday(hire_date)) / 365.25, 1) AS seniority FROM employees WHERE id = ?", (emp_id,))
    return res[0] if res else None

def update_employee(emp_id, emp):
    sql = "UPDATE employees SET name=?, department=?, salary=?, hire_date=?, office_id=? WHERE id=?"
    params = (emp['name'], emp['department'], emp['salary'], emp['hire_date'], emp['office_id'], emp_id)
    query(sql, params, is_select=False)
    
def assign_employees_to_office(office_id, employee_ids):
    if not employee_ids:
        return
    placeholders = ','.join(['?'] * len(employee_ids))
    sql = f"UPDATE employees SET office_id = ? WHERE id IN ({placeholders})"
    params = [office_id] + employee_ids
    query(sql, params, is_select=False)
    


def get_offices(
    floor=0,
    f_type="all",
    min_count=None,
    max_count=None,
    sort_by="id",
    order="asc",
):
    sort_map = {
        "id": "o.id",
        "floor": "o.floor",
        "room_number": "o.room_number",
        "capacity": "o.capacity",
        "current_count": "current_count",
    }
    sort_col = sort_map.get(sort_by, "o.id")
    order_sql = "DESC" if str(order).lower() == "desc" else "ASC"

    sql = f"""
        SELECT o.*, COUNT(e.id) as current_count
        FROM offices o
        LEFT JOIN employees e ON o.id = e.office_id
        WHERE (? = 0 OR o.floor = ?)
        GROUP BY o.id
        HAVING
            ((? = 'all')
                OR (? = 'empty' AND current_count = 0)
                OR (? = 'available' AND current_count < o.capacity)
                OR (? = 'over' AND current_count > o.capacity))
            AND (? IS NULL OR current_count >= ?)
            AND (? IS NULL OR current_count <= ?)
        ORDER BY {sort_col} {order_sql}
    """
    params = (
        floor,
        floor,
        f_type,
        f_type,
        f_type,
        f_type,
        min_count,
        min_count,
        max_count,
        max_count,
    )
    return query(sql, params)

def get_all_offices(floor=0, f_type='all'):
    return get_offices(floor=floor, f_type=f_type)

def add_office(office):
    sql = "INSERT INTO offices (floor, room_number, capacity) VALUES (?, ?, ?)"
    params = (office['floor'], office['room_number'], office['capacity'])
    query(sql, params, is_select=False)
    
def get_office(office_id):
    sql = """
    SELECT offices.*, COUNT(employees.id) AS current_count
    FROM offices
    LEFT JOIN employees ON offices.id = employees.office_id
    WHERE offices.id = ?
    GROUP BY offices.id
    """
    res = query(sql, (office_id,))
    
    if not res:
        return None
        
    office_data = res[0]
    
    office_data['employees'] = query("SELECT * FROM employees WHERE office_id = ?", (office_id,))
    
    return office_data


def delete_office(office_id):
    query("UPDATE employees SET office_id=NULL WHERE office_id = ?", (office_id,), is_select=False)
    query("DELETE FROM offices WHERE id = ?", (office_id,), is_select=False)
    
def update_office(office_id, office):
    sql = "UPDATE offices SET floor=?, room_number=?, capacity=? WHERE id=?"
    params = (office['floor'], office['room_number'], office['capacity'], office_id)
    query(sql, params, is_select=False)

create_tables()

