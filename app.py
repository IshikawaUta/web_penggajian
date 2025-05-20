from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Mengembalikan hasil dalam bentuk dictionary-like
    return conn

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.commit()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initialize the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def index():
    employees = query_db('SELECT id, name, email, salary, address, phone_number, position FROM employees')
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        salary = request.form['salary']
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        position = request.form.get('position')
        query_db('INSERT INTO employees (name, email, salary, address, phone_number, position) VALUES (?, ?, ?, ?, ?, ?)', (name, email, salary, address, phone_number, position))
        return redirect(url_for('index'))
    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = query_db('SELECT * FROM employees WHERE id = ?', (id,), one=True)
    if employee is None:
        return "Karyawan tidak ditemukan."
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        salary = request.form['salary']
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        position = request.form.get('position')
        query_db('UPDATE employees SET name = ?, email = ?, salary = ?, address = ?, phone_number = ?, position = ? WHERE id = ?', (name, email, salary, address, phone_number, position, id))
        return redirect(url_for('index'))
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:id>')
def delete_employee(id):
    query_db('DELETE FROM employees WHERE id = ?', (id,))
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_employee():
    if request.method == 'POST':
        search_term = request.form['search_term']
        employees = query_db('SELECT id, name, email, salary, address, phone_number, position FROM employees WHERE name LIKE ? OR email LIKE ? OR address LIKE ? OR phone_number LIKE ? OR position LIKE ?', ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
        return render_template('search_results.html', employees=employees, search_term=search_term)
    return render_template('search_results.html')

if __name__ == '__main__':
    app.run(debug=True)