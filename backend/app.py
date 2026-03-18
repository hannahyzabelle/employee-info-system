from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary storage (list of employees)
employees = []

# HOME - VIEW ALL EMPLOYEES
@app.route('/')
def index():
    return render_template('index.html', employees=employees)

# ADD EMPLOYEE
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        emp = {
            'id': len(employees) + 1,
            'name': request.form['name'],
            'position': request.form['position'],
            'email': request.form['email']
        }
        employees.append(emp)
        return redirect(url_for('index'))
    return render_template('add.html')

# EDIT EMPLOYEE
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    emp = next((e for e in employees if e['id']'] == id), None)

    if request.method == 'POST':
        emp['name'] = request.form['name']
        emp['position'] = request.form['position']
        emp['email'] = request.form['email']
        return redirect(url_for('index'))

    return render_template('edit.html', emp=emp)

# DELETE EMPLOYEE
@app.route('/delete/<int:id>')
def delete_employee(id):
    global employees
    employees = [e for e in employees if e['id'] != id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)