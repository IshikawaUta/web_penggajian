from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = 'data_karyawan'  # Ganti dengan nama database MongoDB Anda

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

db = get_db()
employees_collection = db['employees']

@app.route('/')
def index():
    employees = list(employees_collection.find())
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        salary = float(request.form['salary'])
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        position = request.form.get('position')

        employee_data = {
            'name': name,
            'email': email,
            'salary': salary,
            'address': address,
            'phone_number': phone_number,
            'position': position
        }

        employees_collection.insert_one(employee_data)
        return redirect(url_for('index'))
    return render_template('add_employee.html')

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = employees_collection.find_one({'_id': ObjectId(id)})
    if employee is None:
        return "Karyawan tidak ditemukan."

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        salary = float(request.form['salary'])
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        position = request.form.get('position')

        updated_data = {
            '$set': {
                'name': name,
                'email': email,
                'salary': salary,
                'address': address,
                'phone_number': phone_number,
                'position': position
            }
        }

        employees_collection.update_one({'_id': ObjectId(id)}, updated_data)
        return redirect(url_for('index'))

    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<string:id>')
def delete_employee(id):
    employees_collection.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_employee():
    if request.method == 'POST':
        search_term = request.form['search_term']
        query = {
            '$or': [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'email': {'$regex': search_term, '$options': 'i'}},
                {'address': {'$regex': search_term, '$options': 'i'}},
                {'phone_number': {'$regex': search_term, '$options': 'i'}},
                {'position': {'$regex': search_term, '$options': 'i'}}
            ]
        }
        employees = list(employees_collection.find(query))
        return render_template('search_results.html', employees=employees, search_term=search_term)
    return render_template('search_results.html')

if __name__ == '__main__':
    app.run(debug=True)