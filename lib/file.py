import os
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from lib.auth import login_required
from .admin import login_required_role
from lib.db import get_db

bp = Blueprint('file', __name__)

# Upload file path
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'lib', 'static', 'uploads', 'audit')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'rtf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/download_audit/<path:filename>')
def download_audit(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@bp.route('/file_type')
def file_type():
    db = get_db()
    file_types = db.execute(
        'SELECT id, name, description FROM audit_File_Type ORDER BY name'
    ).fetchall()
    return render_template('file/file_type.html', file_types=file_types)

@bp.route('/add_file_type', methods=['GET', 'POST'])
def add_file_type():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required!'
        elif not description:
            error = 'Description is required!'
        else:
            db = get_db()
            file_type = db.execute(
                'SELECT id FROM audit_File_Type WHERE name = ?', (name,)
            ).fetchone()
            if file_type is not None:
                error = f'The file type "{name}" already exists.'

        if error is None:
            db.execute(
                'INSERT INTO audit_File_Type (name, description) VALUES (?, ?)',
                (name, description)
            )
            db.commit()
            flash('File type added successfully!')
            return redirect(url_for('file.file_type'))

        flash(error)

    return render_template('file/add_file_type.html')


@bp.route('/edit_file_type/<int:file_type_id>', methods=['GET', 'POST'])
def edit_file_type(file_type_id):
    db = get_db()
    file_type = db.execute(
        'SELECT id, name, description FROM audit_File_Type WHERE id = ?', (file_type_id,)
    ).fetchone()

    if file_type is None:
        abort(404, f"File type id {file_type_id} doesn't exist.")

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
                'UPDATE audit_File_Type SET name = ?, description = ? WHERE id = ?',
               (name, description, file_type_id)
            )
            db.commit()
            flash('File type updated successfully!')
            return redirect(url_for('file.file_type'))

        flash(error)

    return render_template('file/edit_file_type.html', file_type=file_type)

@bp.route('/delete_file_type/<int:file_type_id>', methods=['POST'])
def delete_file_type(file_type_id):
    db = get_db()
    db.execute('DELETE FROM audit_File_Type WHERE id = ?', (file_type_id,))
    db.commit()
    flash('File type deleted successfully!')
    return redirect(url_for('file.file_type'))


@bp.route('/program')
def program():
    db = get_db()
    programs = db.execute('''
        SELECT ap.id, ap.name, ap.period, ap.description, d.name AS division_name, 
            dept.name AS department_name, u.name AS unit_name
        FROM audit_program ap
        LEFT JOIN unit u ON ap.unit_id = u.id
        LEFT JOIN department dept ON ap.department_id = dept.id
        LEFT JOIN division d ON ap.division_id = d.id
        ORDER BY ap.name
    ''').fetchall()
   
    return render_template('file/view_program.html', programs=programs)

@bp.route('/add_program', methods=['GET', 'POST'])
def add_program():
    db = get_db()
    divisions = db.execute('SELECT id, name FROM division ORDER BY name').fetchall()
    departments = db.execute('SELECT id, name FROM department ORDER BY name').fetchall()
    units = db.execute('SELECT id, name FROM unit ORDER BY name').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        period = request.form['period']
        description = request.form['description']
        division_id = request.form.get('division_id')
        department_id = request.form.get('department_id')
        unit_id = request.form.get('unit_id')
        error = None

        if not name:
            error = 'Name is required!'
        elif not period:
            error = 'Period is required!'
        elif not description:
            error = 'Description is required!'
        elif division_id is None and department_id is None and unit_id is None:
            error = 'At least one of Division, Department, or Unit must be selected.'

        if error is None:
            try:
                db.execute(
                    'INSERT INTO audit_program (name, period, description, division_id, department_id, unit_id) VALUES (?, ?, ?, ?, ?, ?)',
                    (name, period, description, division_id, department_id, unit_id)
                )
                db.commit()
                flash('Audit program added successfully!', 'success')
                return redirect(url_for('file.add_program'))
            except db.IntegrityError:
                error = f"The program '{name}' already exists."

        flash(error, 'error')

    return render_template('file/add_program.html', divisions=divisions, departments=departments, units=units)


@bp.route('/edit_program/<int:program_id>', methods=['GET', 'POST'])
def edit_program(program_id):
    db = get_db()
    program = db.execute(
        'SELECT id, name, period, description, division_id, department_id, unit_id FROM audit_program WHERE id = ?',
        (program_id,)
    ).fetchone()

    if program is None:
        flash(f"Program with ID '{program_id}' does not exist.", 'error')
        return redirect(url_for('file.program'))

    divisions = db.execute('SELECT id, name FROM division ORDER BY name').fetchall()
    departments = db.execute('SELECT id, name FROM department ORDER BY name').fetchall()
    units = db.execute('SELECT id, name FROM unit ORDER BY name').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        period = request.form['period']
        description = request.form['description']
        division_id = request.form.get('division_id')
        department_id = request.form.get('department_id')
        unit_id = request.form.get('unit_id')
        error = None

        if not name:
            error = 'Name is required!'
        elif not period:
            error = 'Period is required!'
        elif not description:
            error = 'Description is required!'
        elif division_id is None and department_id is None and unit_id is None:
            error = 'At least one of Division, Department, or Unit must be selected.'

        if error is None:
            try:
                db.execute(
                    'UPDATE audit_program SET name = ?, period = ?, description = ?, division_id = ?, department_id = ?, unit_id = ? WHERE id = ?',
                    (name, period, description, division_id, department_id, unit_id, program_id)
                )
                db.commit()
                flash('Audit program updated successfully!', 'success')
                return redirect(url_for('file.program'))
            except db.IntegrityError:
                error = f"The program '{name}' already exists."

        flash(error, 'error')

    return render_template('file/edit_program.html', program=program, divisions=divisions, departments=departments, units=units)


@bp.route('/delete_program/<int:program_id>', methods=['POST'])
def delete_program(program_id):
    db = get_db()
    db.execute('DELETE FROM audit_program WHERE id = ?', (program_id,))
    db.commit()
    flash('File type deleted successfully!')
    return redirect(url_for('file.program'))