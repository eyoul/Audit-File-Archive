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
AUDIT_FOLDER = os.path.join(os.getcwd(), 'lib', 'static', 'uploads', 'audit')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'rtf'}

if not os.path.exists(AUDIT_FOLDER):
    os.makedirs(AUDIT_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/download_file/<path:filename>')
def download_audit(filename):
    return send_from_directory(AUDIT_FOLDER, filename)

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

@bp.route('/list_file')
def list_file():
    # Get the list of documents with their corresponding document type and division
    db = get_db()
    files = db.execute(
        'SELECT a.id, a.name, a.file_path, a.description, p.name AS audit_program_name, ft.name AS audit_file_Type_name '
        'FROM audit_File a '
        'JOIN audit_program p ON p.id = a.audit_program_id '
        'JOIN audit_File_Type ft ON ft.id = a.file_type_id '
        'ORDER BY a.name'
    ).fetchall()

    return render_template('file/list_file.html', files=files)

@bp.route('/add_file', methods=('GET', 'POST'))
def add_file():
    if request.method == 'POST':     
        # Get the form inputs
        name = request.form['name'].upper()
        description = request.form['description']
        audit_program_id = request.form['audit_program_id']
        file_type_id = request.form['file_type_id']
        
        error = None
        
        # Validate the form inputs
        if not name:
            error = 'Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not audit_program_id:
            error = 'Audit Program is required.'
        elif not file_type_id:
            error = 'File Type is required.'

        # Handle file upload
        if 'file_path' not in request.files:
            error = 'File is required.'
        else:
            file = request.files['file_path']
            if file.filename == '':
                error = 'File is required.'
            elif not allowed_file(file.filename):
                error = 'Invalid file type. Only Pdf, Doc, Docx, Xls, Xlsx, Csv, and Rtf are allowed.'
            else:
                filename = secure_filename(file.filename)
                _, ext = os.path.splitext(filename)
                # Generate a unique filename using uuid4()
                unique_filename = str(uuid.uuid4()) + ext
                file.save(os.path.join(AUDIT_FOLDER, unique_filename))

        # Handle errors and success
        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            # Insert a new record into the "audit_File" table
            cursor.execute(
                'INSERT INTO audit_File (name, file_path, description, audit_program_id, file_type_id, file_size)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (name, unique_filename, description, audit_program_id, file_type_id, os.path.getsize(os.path.join(AUDIT_FOLDER, unique_filename)))
            )
        db.commit()
        flash('File uploaded successfully')
        return redirect(url_for('file.list_file'))
    
    # Render the form
    db = get_db()
    audit_programs = db.execute(
        'SELECT id, name FROM audit_program ORDER BY name'
    ).fetchall()
    file_types = db.execute(
        'SELECT id, name FROM audit_File_Type ORDER BY name'
    ).fetchall()
    return render_template('file/add_file.html', audit_programs=audit_programs, file_types=file_types)


@bp.route('/edit_file/<int:id>', methods=('GET', 'POST'))
def edit_file(id):
    db = get_db()
    file = db.execute(
        'SELECT id, name, file_path, description, audit_program_id, file_type_id '
        'FROM audit_File '
        'WHERE id = ?',
        (id,)
    ).fetchone()

    # Check if the file exists
    if file is None:
        abort(404, f"File id {id} doesn't exist.")

    # Get the current file path
    current_file_path = file['file_path']

    if request.method == 'POST':
        # Get the form inputs
        name = request.form['name'].upper()
        description = request.form['description']
        audit_program_id = request.form['audit_program_id']
        file_type_id = request.form['file_type_id']

        error = None

        # Validate the form inputs
        if not name:
            error = 'Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not audit_program_id:
            error = 'Audit Program is required.'
        elif not file_type_id:
            error = 'File Type is required.'

        # Handle file upload
        if 'file_path' in request.files:
            file = request.files['file_path']
            if file.filename != '':
                if not allowed_file(file.filename):
                    error = 'Invalid file type. Only Pdf, Doc, Docx, Xls, Xlsx, Csv, and Rtf are allowed.'
                else:
                    filename = secure_filename(file.filename)
                    _, ext = os.path.splitext(filename)
                    # Generate a unique filename using uuid4()
                    unique_filename = str(uuid.uuid4()) + ext
                    file.save(os.path.join(AUDIT_FOLDER, unique_filename))

                    # Remove the old file from the upload folder
                    os.remove(os.path.join(AUDIT_FOLDER, current_file_path))

                    # Update the file path with the new filename
                    current_file_path = unique_filename

        # Handle errors and success
        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE audit_File SET name = ?, file_path = ?, description = ?, '
                'audit_program_id = ?, file_type_id = ?, file_size = ? WHERE id = ?',
                (name, current_file_path, description, audit_program_id, file_type_id, os.path.getsize(os.path.join(AUDIT_FOLDER, current_file_path)), id)
            )
            db.commit()

            flash('File updated successfully')
            return redirect(url_for('file.list_file'))

    # Render the form
    audit_programs = db.execute(
        'SELECT id, name FROM audit_program ORDER BY name'
    ).fetchall()
    file_types = db.execute(
        'SELECT id, name FROM audit_File_Type ORDER BY name'
    ).fetchall()
    return render_template('file/edit_file.html', file=file, audit_programs=audit_programs, file_types=file_types)


@bp.route('/delete_file/<int:id>', methods=('POST',))
def delete_file(id):
    db = get_db()
    file = db.execute(
        'SELECT id, file_path FROM audit_File WHERE id = ?', (id,)
    ).fetchone()
    if file is None:
        abort(404, f"File id {id} doesn't exist.")

    # Delete the record from the "audit_File" table
    db.execute(
        'DELETE FROM audit_File WHERE id = ?', (id,)
    )
    db.commit()

    # Delete the file from the upload folder
    os.remove(os.path.join(AUDIT_FOLDER, file['file_path']))

    flash('File deleted successfully')
    return redirect(url_for('file.list_file'))