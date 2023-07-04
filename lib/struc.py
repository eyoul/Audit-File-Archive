from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lib.auth import login_required
from lib.db import get_db

bp = Blueprint('struc', __name__)

# Add Division
@bp.route('/add_division', methods=['GET', 'POST'])        
def add_division():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        db = get_db()
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description Id required!'
     
        if error is None:
            try:
                db.execute(
                    "INSERT INTO division (name, description) VALUES (?, ?)",
                    (name, description),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Division {name} is already registered."
            else:
                return redirect(url_for('struc.add_division'))
            flash(error)
    
    return render_template('admin/add_div.html')

# Add Department
@bp.route('/add_department', methods=['GET', 'POST'])        
def add_department():
    db = get_db()
    divisions = db.execute('SELECT id, name FROM division ORDER BY name').fetchall()

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
                
        if error is None:
            try:
                db.execute(
                    "INSERT INTO department (name, description, division_id) VALUES (?, ?, ?)",
                    (name, description, division_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Department {name} is already registered."
            else:
                return redirect(url_for('struc.add_department'))
            flash(error)
    
    return render_template('admin/add_dep.html', divisions=divisions)


#Add Unit
@bp.route('/add_unit', methods=['GET', 'POST'])        
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
                    "INSERT INTO department (name, description, department_id) VALUES (?, ?, ?)",
                    (name, description, department_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Department {name} is already registered."
            else:
                return redirect(url_for('struc.add_unit'))
            flash(error)
    
    return render_template('admin/add_unit.html', departments=departments)

@bp.route('/display_structure', methods=['GET', 'POST'])
def display_structure():
    db = get_db()
    divisions = db.execute('SELECT * FROM division ORDER BY name').fetchall()
    departments = db.execute('SELECT * FROM department ORDER BY name').fetchall()
    units = db.execute('SELECT * FROM unit ORDER BY name').fetchall()
    return render_template('admin/display_structure.html', divisions=divisions, departments=departments, units=units)