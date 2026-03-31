import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

# Point Flask to the frontend directories
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))
app.secret_key = 'super-secret-key-for-session'

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open(os.path.join(os.path.dirname(__file__), 'db.sql'), 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

init_db()

# ================= LOGIN =================
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            flash("Invalid credentials, please try again.")
            return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

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
    if 'user_id' not in session:
        return redirect('/')

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
    if 'user_id' not in session:
        return redirect('/')

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
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db()

    emp = conn.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()

    conn.close()

    if emp is None:
        return "Employee not found", 404

    return render_template('employee-info.html', emp=emp)


# ================= UPDATE EMPLOYEE =================
@app.route('/update_employee/<int:id>', methods=['POST'])
def update_employee(id):
    if 'user_id' not in session:
        return redirect('/')

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
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db()

    conn.execute("DELETE FROM employees WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/employees')


# ================= EMPLOYEE INFO SHORTCUT =================
@app.route('/employee-info')
def employee_info_redirect():
    if 'user_id' not in session:
        return redirect('/')

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
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db()
    data = conn.execute("SELECT * FROM trainings").fetchall()
    conn.close()
    return render_template('trainings.html', trainings=data)

@app.route('/add_training', methods=['POST'])
def add_training():
    if 'user_id' not in session:
        return redirect('/')

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
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db()

    conn.execute("DELETE FROM trainings WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/trainings')


# ================= SERVICE RECORD =================
@app.route('/service-record')
def service():
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db()
    data = conn.execute("SELECT * FROM service_record").fetchall()
    conn.close()
    return render_template('service-record.html', records=data)

@app.route('/add_service', methods=['POST'])
def add_service():
    if 'user_id' not in session:
        return redirect('/')

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
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db()

    conn.execute("DELETE FROM service_record WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/service-record')


# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)