from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Employees Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        birthday TEXT,
        status TEXT
    )
    ''')

    # Trainings Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trainings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        title TEXT,
        date TEXT
    )
    ''')

    # Service Record Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        position TEXT,
        start_date TEXT,
        end_date TEXT,
        agency TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ================= LOGIN =================
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '1234':
            return redirect('/dashboard')
        else:
            return "Invalid Credentials"

    return render_template('login.html')


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    active = total
    permanent = conn.execute("SELECT COUNT(*) FROM employees WHERE status='Permanent'").fetchone()[0]
    temporary = conn.execute("SELECT COUNT(*) FROM employees WHERE status='Temporary'").fetchone()[0]
    separated = conn.execute("SELECT COUNT(*) FROM employees WHERE status='Separated'").fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total=total,
        active=active,
        permanent=permanent,
        temporary=temporary,
        separated=separated
    )


# ================= EMPLOYEES =================
@app.route('/employees')
def employees():
    search = request.args.get('search','')

    conn = get_db()

    if search:
        data = conn.execute("""
            SELECT * FROM employees
            WHERE first_name LIKE ? OR last_name LIKE ?
        """, ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        data = conn.execute("SELECT * FROM employees").fetchall()

    conn.close()

    return render_template('employee-list.html', employees=data, search=search)


# ================= ADD EMPLOYEE =================
@app.route('/add_employee', methods=['POST'])
def add_employee():
    conn = get_db()

    conn.execute("""
        INSERT INTO employees (first_name, last_name, birthday, status)
        VALUES (?, ?, ?, ?)
    """, (
        request.form['first_name'],
        request.form['last_name'],
        request.form['birthday'],
        request.form['status']
    ))

    conn.commit()
    conn.close()

    return redirect('/employees')


# ================= VIEW / EDIT EMPLOYEE =================
@app.route('/employee/<int:id>')
def view_employee(id):
    conn = get_db()

    emp = conn.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()

    conn.close()

    if emp is None:
        return "Employee not found", 404

    return render_template('employee-info.html', emp=emp)


# ================= UPDATE EMPLOYEE =================
@app.route('/update_employee/<int:id>', methods=['POST'])
def update_employee(id):
    conn = get_db()

    conn.execute("""
        UPDATE employees
        SET first_name=?, last_name=?, birthday=?, status=?
        WHERE id=?
    """, (
        request.form['first_name'],
        request.form['last_name'],
        request.form['birthday'],
        request.form['status'],
        id
    ))

    conn.commit()
    conn.close()

    return redirect('/employees')


# ================= DELETE EMPLOYEE =================
@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    conn = get_db()

    conn.execute("DELETE FROM employees WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/employees')


# ================= EMPLOYEE INFO SHORTCUT =================
@app.route('/employee-info')
def employee_info_redirect():
    conn = get_db()
    emp = conn.execute("SELECT id FROM employees ORDER BY id LIMIT 1").fetchone()
    conn.close()

    if emp:
        return redirect(f"/employee/{emp['id']}")
    else:
        return "No employees found", 404


# ================= TRAININGS =================
@app.route('/trainings')
def trainings():
    conn = get_db()
    data = conn.execute("SELECT * FROM trainings").fetchall()
    conn.close()
    return render_template('trainings.html', trainings=data)

@app.route('/add_training', methods=['POST'])
def add_training():
    conn = get_db()

    conn.execute("""
        INSERT INTO trainings (employee_id, title, date)
        VALUES (?, ?, ?)
    """, (
        request.form['employee_id'],
        request.form['title'],
        request.form['date']
    ))

    conn.commit()
    conn.close()

    return redirect('/trainings')

@app.route('/delete_training/<int:id>')
def delete_training(id):
    conn = get_db()

    conn.execute("DELETE FROM trainings WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/trainings')


# ================= SERVICE RECORD =================
@app.route('/service-record')
def service():
    conn = get_db()
    data = conn.execute("SELECT * FROM service_record").fetchall()
    conn.close()
    return render_template('service-record.html', records=data)

@app.route('/add_service', methods=['POST'])
def add_service():
    conn = get_db()

    conn.execute("""
        INSERT INTO service_record (employee_id, position, start_date, end_date, agency)
        VALUES (?, ?, ?, ?, ?)
    """, (
        request.form['employee_id'],
        request.form['position'],
        request.form['start'],
        request.form['end'],
        request.form['agency']
    ))

    conn.commit()
    conn.close()

    return redirect('/service-record')

@app.route('/delete_service/<int:id>')
def delete_service(id):
    conn = get_db()

    conn.execute("DELETE FROM service_record WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/service-record')


# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)