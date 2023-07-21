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
    divisions = db.execute(
        'SELECT id, name, description FROM division ORDER BY name'
    ).fetchall()
    return render_template('admin/division.html', divisions=divisions)


@bp.route('/add_division', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def add_division():
    db = get_db()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'

        if error is None:
            existing_division = db.execute(
                'SELECT id FROM division WHERE name = ?', (name,)
            ).fetchone()

            if existing_division is not None:
                flash(f"The division '{name}' already exists.")
            else:
                db.execute(
                    'INSERT INTO division (name, description) VALUES (?, ?)',
                    (name, description)
                )
                db.commit()
                flash('Division added successfully!')
                return redirect(url_for('struc.division'))

        flash(error)

    divisions = db.execute(
        'SELECT id, name, description FROM division'
    ).fetchall()

    return render_template('admin/add_div.html', divisions=divisions)


@bp.route('/edit_division/<int:division_id>', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def edit_division(division_id):
    db = get_db()
    division = db.execute(
        'SELECT id, name, description FROM division WHERE id = ?', (division_id,)
    ).fetchone()

    if division is None:
        abort(404, f"Division id {division_id} doesn't exist.")

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'

        if error is None:
            db.execute(
                'UPDATE division SET name = ?, description = ? WHERE id = ?',
               (name, description, division_id)
            )
            db.commit()
            flash('Division updated successfully!')
            return redirect(url_for('struc.division'))

        flash(error)

    return render_template('admin/edit_div.html', division=division)


@bp.route('/delete_division/<int:division_id>', methods=['POST'])
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_division(division_id):
    db = get_db()

    # Use a transaction to ensure that the deletion is atomic
    with db:
        # Delete the division record and any associated department records
        db.execute('DELETE FROM division WHERE id = ?', (division_id,))

    flash('Division deleted successfully!')
    return redirect(url_for('struc.add_division'))


# Department
@bp.route('/department')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def department():
    db = get_db()
    departments = db.execute(
        'SELECT d.id, d.name, d.description, dv.name AS division_name '
        'FROM department d JOIN division dv ON d.division_id = dv.id '
        'ORDER BY d.name'
    ).fetchall()

    return render_template('admin/departments.html', departments=departments)

@bp.route('/add_department', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def add_department():
    db = get_db()

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
                'SELECT id FROM department WHERE name = ?', (name,)
        ).fetchone() is not None:
            error = f"Department '{name}' already exists!"

        if error is None:
            db.execute(
                'INSERT INTO department (name, description, division_id) VALUES (?, ?, ?)',
                (name, description, division_id)
            )
            db.commit()
            flash('Department added successfully!')
            return redirect(url_for('struc.department'))

        flash(error)

    divisions = db.execute('SELECT id, name FROM division ORDER BY name').fetchall()
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
    units = db.execute(
        'SELECT u.id, u.name, u.description, d.name AS department_name, dv.name AS division_name '
        'FROM unit u JOIN department d ON u.department_id = d.id '
        'JOIN division dv ON d.division_id = dv.id '
        'ORDER BY u.name'
    ).fetchall()

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
