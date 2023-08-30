from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lib.auth import login_required
from .admin import login_required_role

from lib.db import get_db

bp = Blueprint('struc', __name__)


@bp.route('/admin/dashboard')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def dashboard():
    db = get_db()
    divisions = db.execute('SELECT * FROM division ORDER BY name').fetchall()
    return render_template('admin/dashboard.html', divisions=divisions)

# Division
@bp.route('/division')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def division():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM division ORDER BY name')
    divisions = cursor.fetchall()

    cursor.close()

    return render_template('admin/division.html', divisions=divisions)


@bp.route('/add_division', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def add_division():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'

        if error is None:
            cursor.execute(
                'SELECT id FROM division WHERE name = %s', (name,)
            )
            existing_division = cursor.fetchone()

            if existing_division is not None:
                flash(f"The division '{name}' already exists.")
            else:
                cursor.execute(
                    'INSERT INTO division (name, description) VALUES (%s, %s)',
                    (name, description)
                )
                db.commit()
                flash('Division added successfully!')
                return redirect(url_for('struc.division'))

        flash(error)

    cursor.execute(
        'SELECT id, name, description FROM division'
    )
    divisions = cursor.fetchall()

    cursor.close()

    return render_template('admin/add_div.html', divisions=divisions)


@bp.route('/edit_division/<int:division_id>', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def edit_division(division_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'SELECT id, name, description FROM division WHERE id = %s', (division_id,)
    )
    division = cursor.fetchone()

    if division is None:
        flash(f"Division id {division_id} doesn't exist.")
        return redirect(url_for('struc.division'))

    division_id, name, description = division

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'

        if error is None:
            cursor.execute(
                'UPDATE division SET name = %s, description = %s WHERE id = %s',
                (name, description, division_id)
            )
            db.commit()
            flash('Division updated successfully!')
            return redirect(url_for('struc.division'))

        flash(error)

    cursor.close()

    return render_template('admin/edit_div.html', division={'id': division_id, 'name': name, 'description': description})


@bp.route('/delete_division/<int:division_id>', methods=['POST'])
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_division(division_id):
    db = get_db()
    cursor = db.cursor()

    # Use a transaction to ensure that the deletion is atomic
    with db:
        # Delete the division record and any associated department records
        cursor.execute('DELETE FROM division WHERE id = %s', (division_id,))
    cursor.close()

    flash('Division deleted successfully!')
    return redirect(url_for('struc.division'))


# Department
@bp.route('/department')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def department():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'SELECT d.id, d.name, d.description, dv.name AS division_name '
        'FROM department d JOIN division dv ON d.division_id = dv.id '
        'ORDER BY d.name'
    )
    departments = cursor.fetchall()

    cursor.close()

    return render_template('admin/departments.html', departments=departments)


@bp.route('/add_department', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def add_department():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        division_id = request.form['division_id']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'
        elif not division_id:
            error = 'Division is required!'
        else:
            db = get_db()
            cursor = db.cursor()

            # Check if the department already exists
            cursor.execute('SELECT id FROM department WHERE name = %s', (name,))
            department = cursor.fetchone()

            if department:
                error = f"Department '{name}' already exists!"

            if error is None:
                # Insert the department into the database
                cursor.execute(
                    'INSERT INTO department (name, description, division_id) VALUES (%s, %s, %s)',
                    (name, description, division_id)
                )
                db.commit()
                flash('Department added successfully!')
                cursor.close()
                return redirect(url_for('struc.department'))

            cursor.close()
            flash(error)

    db = get_db()
    cursor = db.cursor()

    # Fetch the divisions for displaying in the template
    cursor.execute('SELECT id, name FROM division ORDER BY name')
    divisions = cursor.fetchall()
  
    cursor.close()
    return render_template('admin/add_dep.html', divisions=divisions)


@bp.route('/edit_department/<int:department_id>', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def edit_department(department_id):
    db = get_db()
    department = db.execute(
        'SELECT id, name, description, division_id FROM department WHERE id = ?', (department_id,)
    ).fetchone()

    if department is None:
        abort(404, f"Department id {department_id} doesn't exist.")

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        division_id = request.form['division_id']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'
        elif not division_id:
            error = 'Division is required!'
        elif db.execute(
                'SELECT id FROM department WHERE name = ? AND id != ?', (name, department_id)
        ).fetchone() is not None:
            error = f"Department '{name}' already exists!"

        if error is None:
            db.execute(
                'UPDATE department SET name = ?, description = ?, division_id = ? WHERE id = ?',
                (name, description, division_id, department_id)
            )
            db.commit()
            flash('Department updated successfully!')
            return redirect(url_for('struc.department'))

        flash(error)

    divisions = db.execute('SELECT id, name FROM division ORDER BY name').fetchall()
    return render_template('admin/edit_dep.html', department=department, divisions=divisions)

@bp.route('/delete_department/<int:department_id>', methods=['POST'])
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_department(department_id):
    db = get_db()

    # Use a transaction to ensure that the deletion is atomic
    with db:
        # Delete the division record and any associated department records
        db.execute('DELETE FROM department WHERE id = ?', (department_id,))

    db.commit()
    flash('Department deleted successfully!')
    return redirect(url_for('struc.department'))
 

#Unit
@bp.route('/unit')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def unit():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'SELECT u.id, u.name, u.description, d.name AS department_name, dv.name AS division_name '
        'FROM unit u JOIN department d ON u.department_id = d.id '
        'JOIN division dv ON d.division_id = dv.id '
        'ORDER BY u.name'
    )
    units = cursor.fetchall()

    cursor.close()
    return render_template('admin/units.html', units=units)


@bp.route('/add_unit', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def add_unit():
    db = get_db()
    departments = db.execute('SELECT id, name FROM department ORDER BY name').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        department_id = request.form['department_id']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'
        elif not department_id:
            error = 'Department is required!'
                
        if error is None:
            try:
                db.execute(
                    "INSERT INTO unit (name, description, department_id) VALUES (?, ?, ?)",
                    (name, description, department_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Unit {name} is already registered."
            else:
                flash('The unit has been added.', 'success')
                return redirect(url_for('struc.unit'))
            
        flash(error, 'error')
    
    return render_template('admin/add_unit.html', departments=departments)


@bp.route('/edit_unit/<int:unit_id>', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def edit_unit(unit_id):
    db = get_db()
    unit = db.execute(
        'SELECT id, name, description, department_id FROM unit WHERE id = ?', (unit_id,)
    ).fetchone()

    if unit is None:
        abort(404, f"Unit id {unit_id} doesn't exist.")

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        department_id = request.form['department_id']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'
        elif not department_id:
            error = 'Division is required!'
        elif db.execute(
                'SELECT id FROM unit WHERE name = ? AND id != ?', (name, unit_id)
        ).fetchone() is not None:
            error = f"Unit '{name}' already exists!"

        if error is None:
            db.execute(
                'UPDATE unit SET name = ?, description = ?, department_id = ? WHERE id = ?',
                (name, description, department_id, unit_id)
            )
            db.commit()
            flash('Unit updated successfully!')
            return redirect(url_for('struc.unit'))

        flash(error)

    departments = db.execute('SELECT id, name FROM department ORDER BY name').fetchall()
    return render_template('admin/edit_unit.html', unit=unit, departments=departments)


@bp.route('/unit/<int:unit_id>/delete', methods=('POST',))
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_unit(unit_id):
    db = get_db()
    
    # Use a transaction to ensure that the deletion is atomic
    with db:
        # Delete the division record and any associated department records
        db.execute('DELETE FROM unit WHERE id = ?', (unit_id,))

    db.commit()
    return redirect(url_for('struc.unit'))


@bp.route('/display_structure', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def display_structure():
    db = get_db()
    divisions = db.execute('SELECT * FROM division ORDER BY name').fetchall()
    departments = db.execute('SELECT * FROM department ORDER BY name').fetchall()
    units = db.execute('SELECT * FROM unit ORDER BY name').fetchall()
    return render_template('admin/display_structure.html', divisions=divisions, departments=departments, units=units)

