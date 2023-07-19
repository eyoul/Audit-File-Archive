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

    return render_template('admin/edit_file_type.html', file_type=file_type)

@bp.route('/delete_file_type/<int:file_type_id>', methods=['POST'])
def delete_file_type(file_type_id):
    db = get_db()
    db.execute('DELETE FROM audit_File_Type WHERE id = ?', (file_type_id,))
    db.commit()
    flash('File type deleted successfully!')
    return redirect(url_for('file.file_type'))



@bp.route('/<int:audit_report_id>/files')
def view_audit(audit_report_id):
    db = get_db()
    audit_report = db.execute('SELECT * FROM audit_report WHERE id = ?', (audit_report_id,)).fetchone()
    if not audit_report:
        abort(404)

    files = db.execute(
        'SELECT f.id, f.description, f.filepath, ft.name AS file_type '
        'FROM file AS f JOIN file_type AS ft ON f.file_type_id = ft.id '
        'WHERE f.audit_report_id = ?',
        (audit_report_id,)
    ).fetchall()

    return render_template('file/view_audit.html', audit_report=audit_report, files=files)


@bp.route('/add_file', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        audit_report_id = request.form['audit_report_id']
        file_type_id = request.form['file_type_id']
        description = request.form['description']
        file = request.files['file']
        error = None

        if not audit_report_id:
            error = 'Audit report ID is required!'
        elif not file_type_id:
            error = 'File type ID is required!'

        elif not description:
            error = 'Description is required!'
        elif file.filename == '':
            error = 'No file selected!'
        elif not allowed_file(file.filename):
            error = f'Invalid file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'

        if error is None:
            # Generate a unique filename and save the file to disk
            filename = f'{uuid.uuid4()}.{secure_filename(file.filename.rsplit(".", 1)[1])}'
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            # Insert the file record into the database
            db = get_db()
            db.execute(
                'INSERT INTO audit_File (name, file_path, description, audit_report_id, file_type_id, file_size) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (file.filename, filename, description, audit_report_id, file_type_id, os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)))
            )
            db.commit()
            flash('File added successfully!')
            return redirect(url_for('audit.view_audit', audit_id=audit_report_id))

        flash(error)

    db = get_db()
    audit_reports = db.execute(
        'SELECT id, audit_period FROM audit_Report ORDER BY audit_period DESC'
    ).fetchall()
    file_types = db.execute(
        'SELECT id, name FROM audit_File_Type ORDER BY name'
    ).fetchall()
    return render_template('file/add_file.html', audit_reports=audit_reports, file_types=file_types)


@bp.route('/edit_file/<int:file_id>', methods=['GET', 'POST'])
def edit_file(file_id):
    db = get_db()
    file = db.execute(
        'SELECT id, name, file_path, description, audit_report_id, file_type_id FROM audit_File WHERE id = ?', (file_id,)
    ).fetchone()

    if file is None:
        abort(404, f"File id {file_id} doesn't exist.")

    if request.method == 'POST':
        audit_report_id = request.form['audit_report_id']
        file_type_id = request.form['file_type_id']
        description = request.form['description']
        error = None

        if not audit_report_id:
            error = 'Audit report ID is required!'
        elif not file_type_id:
            error = 'File type ID is required!'
        elif not description:
            error = 'Description is required!'

        if error is None:
            db.execute(
                'UPDATE audit_File SET description = ?, audit_report_id = ?, file_type_id = ? WHERE id = ?',
               (description, audit_report_id, file_type_id, file_id)
            )
            db.commit()
            flash('File updated successfully!')
            return redirect(url_for('audit.view_audit', audit_id=audit_report_id))

        flash(error)

    audit_reports = db.execute(
        'SELECT id, audit_period FROM audit_Report ORDER BY audit_period DESC'
    ).fetchall()
    file_types = db.execute(
        'SELECT id, name FROM audit_File_Type ORDER BY name'
    ).fetchall()
    return render_template('file/edit_file.html', file=file, audit_reports=audit_reports, file_types=file_types)


@bp.route('/delete_file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    db = get_db()
    file = db.execute(
        'SELECT id, file_path, audit_report_id FROM audit_File WHERE id = ?', (file_id,)
    ).fetchone()

    if file is None:
        abort(404, f"File id {file_id} doesn't exist.")

    # Delete the file from disk
    os.remove(os.path.join(UPLOAD_FOLDER, file['file_path']))

    # Delete the file record from the database
    db.execute('DELETE FROM audit_File WHERE id = ?', (file_id,))
    db.commit()
    flash('File deleted successfully!')
    return redirect(url_for('audit.view_audit', audit_id=file['audit_report_id']))


@bp.route('/division/<int:division_id>/audit/add_file', methods=['GET', 'POST'])
@login_required
def add_file_to_division_audit(division_id):
    db = get_db()
    division = db.execute(
        'SELECT id, name FROM division WHERE id = ?', (division_id,)
    ).fetchone()

    if division is None:
        abort(404, f"Division id {division_id} doesn't exist.")

    if request.method == 'POST':
        file_type_id = request.form['file_type']
        description = request.form['description']
        file = request.files['file']
        error = None

        if not file.filename:
            error = 'No file selected!'
        elif not allowed_file(file.filename):
            error = 'Invalid file type!'
        elif not description:
            error = 'Description is required!'
        else:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_AUDIT_FOLDER'], filename)
            file.save(file_path)
            audit_report_id = db.execute(
                'INSERT INTO audit_Report (audit_period, file_directory) VALUES (?, ?)',
                ('2023-07', app.config['UPLOAD_AUDIT_FOLDER'])
            ).lastrowid
            file_size = os.path.getsize(file_path)
            db.execute(
                'INSERT INTO audit_File (name, file_path, description, audit_report_id, file_type_id, file_size, division_id) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (filename, file_path, description, audit_report_id, file_type_id, file_size, division_id)
            )
            db.commit()
            audit_file_id = db.execute(
                'SELECT id FROM audit_File WHERE name = ?', (filename,)
            ).fetchone()['id']
            db.execute(
                'INSERT INTO division_audit_File (audit_file_id, division_id) VALUES (?, ?)',
                (audit_file_id, division_id)
            )
            db.commit()
            flash('File added successfully!', 'success')
            return redirect(url_for('division.division_detail', division_id=division_id))

        flash(error, 'error')

    file_types = db.execute(
        'SELECT id, name FROM audit_File_Type ORDER BY name'
    ).fetchall()
    return render_template('add_division_audit_file.html', division=division, file_types=file_types)