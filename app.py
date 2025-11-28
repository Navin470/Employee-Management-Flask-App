from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'mysecretkey123456'


# ==================== DATABASE CONNECTION ====================
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',           # XAMPP default (empty password)
            database='employee_db'
        )
        return conn
    except Error as e:
        print(f"Connection failed: {e}")
        return None


# ==================== HOME PAGE ====================
@app.route('/')
def index():
    conn = get_db_connection()
    if not conn or not conn.is_connected():
        flash('Cannot connect to database!', 'danger')
        return render_template('index.html', employees=[])

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees ORDER BY id DESC")
        employees = cursor.fetchall()
        return render_template('index.html', employees=employees)
    except Error as e:
        flash(f'Error fetching data: {e}', 'danger')
        return render_template('index.html', employees=[])
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


# ==================== ADD EMPLOYEE ====================
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('add_employee'))

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO employees (name, email, phone, department) VALUES (%s, %s, %s, %s)",
                (name, email, phone, department)
            )
            conn.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('index'))
        except Error as e:
            conn.rollback()
            flash(f'Error: {e}', 'danger')
        finally:
            if cursor:
                cursor.close()
            if conn.is_connected():
                conn.close()

    return render_template('add.html')


# ==================== EDIT EMPLOYEE ====================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed!', 'danger')
        return redirect(url_for('index'))

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            department = request.form['department']

            cursor.execute(
                "UPDATE employees SET name=%s, email=%s, phone=%s, department=%s WHERE id=%s",
                (name, email, phone, department, id)
            )
            conn.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('index'))

        # GET: show edit form
        cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
        employee = cursor.fetchone()

        if not employee:
            flash('Employee not found!', 'danger')
            return redirect(url_for('index'))

        return render_template('edit.html', employee=employee)

    except Error as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


# ==================== DELETE EMPLOYEE ====================
@app.route('/delete/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    if not conn:
        flash('Database error!', 'danger')
        return redirect(url_for('index'))

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
        conn.commit()
        flash('Employee deleted successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error deleting: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

    return redirect(url_for('index'))   # Fixed the typo here!


# ==================== RUN APP ====================
if __name__ == '__main__':
    app.run(debug=True, port=5500)