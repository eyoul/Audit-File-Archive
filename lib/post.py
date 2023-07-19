import os
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lib.auth import login_required
from .admin import login_required_role
from lib.db import get_db

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flask import send_from_directory


bp = Blueprint('post', __name__)


#Upload file path
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'lib', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'rtf' }

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    return render_template('post/index.html')


@bp.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@bp.route('/board')
def board():
    db = get_db()
    divisions = db.execute(
        'SELECT id, name, description FROM division'
    ).fetchall()

    departments = db.execute(
        'SELECT id, name, description, division_id FROM department'
    ).fetchall()

    units = db.execute(
        'SELECT id, name, description, department_id FROM unit'
    ).fetchall()

    documents = db.execute(
        'SELECT id, name, file_path, description, docType_id, division_id, department_id, unit_id FROM document'
    ).fetchall()
    
    programs = db.execute(
        'SELECT id, name, period, description, division_id, department_id, unit_id FROM audit_program'
    ).fetchall()
    audit_files = db.execute('''
    SELECT audit_File.*, audit_File_Type.name AS type_name
    FROM audit_File
    JOIN audit_File_Type ON audit_File.file_type_id = audit_File_Type.id
    ORDER BY audit_File.name
    ''').fetchall()

    return render_template('post/board.html', divisions=divisions, departments=departments,
                           units=units, documents=documents, programs=programs, audit_files=audit_files)


@bp.route('/docType')
def docType():
    db = get_db()
    docTypes = db.execute(
        'SELECT id, name, description FROM docType ORDER BY name'
    ).fetchall()
    return render_template('admin/docTypes.html', docTypes=docTypes)


@bp.route('/add_doc_type', methods=['GET', 'POST'])
def add_doc_type():
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
            doc_type = db.execute(
                'SELECT id FROM docType WHERE name = ?', (name,)
            ).fetchone()
            if doc_type is not None:
                error = f'The document type "{name}" already exists.'

        if error is None:
            db.execute(
                'INSERT INTO docType (name, description) VALUES (?, ?)',
                (name, description)
            )
            db.commit()
            flash('Document type added successfully!')
            return redirect(url_for('post.docType'))

        flash(error)

    return render_template('admin/add_doc_type.html')


@bp.route('/edit_doc_type/<int:doc_type_id>', methods=['GET', 'POST'])
def edit_doc_type(doc_type_id):
    db = get_db()
    doc_type = db.execute(
        'SELECT id, name, description FROM docType WHERE id = ?', (doc_type_id,)
    ).fetchone()

    if doc_type is None:
        abort(404, f"Document type id {doc_type_id} doesn't exist.")

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
                'UPDATE docType SET name = ?, description = ? WHERE id = ?',
               (name, description, doc_type_id)
            )
            db.commit()
            flash('Document type updated successfully!')
            return redirect(url_for('post.docType'))

        flash(error)

    return render_template('admin/edit_doc_type.html', doc_type=doc_type)


@bp.route('/delete_doc_type/<int:doc_type_id>', methods=['POST'])
def delete_doc_type(doc_type_id):
    db = get_db()
    db.execute('DELETE FROM docType WHERE id = ?', (doc_type_id,))
    db.commit()
    flash('Document type deleted successfully!')
    return redirect(url_for('post.docType'))


@bp.route('/add_div_file', methods=('GET', 'POST'))
def add_div_file():
    # Get the list of document types to populate the select element
    db = get_db()
    docTypes = db.execute(
        'SELECT id, name FROM docType ORDER BY name'
    ).fetchall()

    # Get the list of divisions to populate the select element
    divisions = db.execute(
        'SELECT id, name FROM division ORDER BY name'
    ).fetchall()

    # Handle form submission
    if request.method == 'POST':
        # Extract form inputs
        name = request.form['name'].upper()
        description = request.form['description']
        docType_id = request.form['docType_id']     
        division_id = request.form['division_id']
        
        error = None

        # Validate form inputs
        if not name:
            error = 'Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not docType_id:
            error = 'Document Type is required.'
        elif not division_id:
            error = 'Division is required.'
                
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
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                
        # Handle errors and success
        if error is not None: 
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            # Insert the document into the document table
            cursor.execute(
               'INSERT INTO document (name, file_path, description, docType_id, division_id)'
               ' VALUES (?, ?, ?, ?, ?)',
                (name, unique_filename, description, docType_id, division_id)
            )

            doc_id = cursor.lastrowid

            # Insert the document into the division_document table
            cursor.execute(
                'INSERT INTO division_document (division_id, document_id)'
                ' VALUES (?, ?)',
                (division_id, doc_id)
            )
                     
            db.commit()
            flash('File added successfully!')
            return redirect(url_for('post.add_div_file'))

    return render_template('admin/add_div_file.html', docTypes=docTypes, 
                           divisions=divisions)


@bp.route('/add_dep_file', methods=('GET', 'POST'))
def add_dep_file():
    # Get the list of document types to populate the select element
    db = get_db()
    docTypes = db.execute(
        'SELECT id, name FROM docType ORDER BY name'
    ).fetchall()

    # Get the list of departments to populate the select element
    departments = db.execute(
        'SELECT id, name FROM department ORDER BY name'
    ).fetchall()

    # Handle form submission
    if request.method == 'POST':
        # Extract form inputs
        name = request.form['name'].upper()
        description = request.form['description']
        docType_id = request.form['docType_id']
        department_id = request.form['department_id']
        
        error = None

        # Validate form inputs
        if not name:
            error = 'Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not docType_id:
            error = 'Document Type is required.'
        elif not department_id:
            error = 'Department is required.'
        
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
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                
        # Handle errors and success
        if error is not None: 
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            # Insert the document into the document table

            cursor.execute(
               'INSERT INTO document (name, file_path, description, docType_id, department_id)'
               ' VALUES (?, ?, ?, ?, ?)',
                (name, unique_filename, description, docType_id, department_id)
            )
            doc_id = cursor.lastrowid

            # Insert the document into the department_document table
            cursor.execute(
                'INSERT INTO department_document (department_id, document_id)'
                ' VALUES (?, ?)',
                (department_id, doc_id)
            )

            db.commit()
            flash('File added successfully!')
            return redirect(url_for('post.add_dep_file'))

    return render_template('admin/add_dep_file.html', docTypes=docTypes, 
                            departments=departments)


@bp.route('/add_unit_file', methods=('GET', 'POST'))
def add_unit_file():
    # Get the list of document types to populate the select element
    db = get_db()
    docTypes = db.execute(
        'SELECT id, name FROM docType ORDER BY name'
    ).fetchall()

    # Get the list of units to populate the select element
    units = db.execute(
        'SELECT id, name FROM unit ORDER BY name'
    ).fetchall()

    # Handle form submission
    if request.method == 'POST':
        # Extract form inputs
        name = request.form['name'].upper()
        description = request.form['description']
        docType_id = request.form['docType_id']
        unit_id = request.form['unit_id']

        error = None

        # Validate form inputs
        if not name:
            error = 'Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not docType_id:
            error = 'Document Type is required.'
        elif not unit_id:
            error = 'Unit is required.'
        
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
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                
        # Handle errors and success
        if error is not None: 
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            # Insert the document into the document table
            cursor.execute(
                'INSERT INTO document (name, file_path, description, docType_id, unit_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, unique_filename, description, docType_id, unit_id)
            )

            doc_id = cursor.lastrowid

            # Insert the document into the unit_document table
            cursor.execute(
                'INSERT INTO unit_document (unit_id, document_id)'
                ' VALUES (?, ?)',
                (unit_id, doc_id)
            )

            db.commit()
            flash('File added successfully!')
            return redirect(url_for('post.add_unit_file'))

    return render_template('admin/add_unit_file.html', docTypes=docTypes, units=units)

@bp.route('/view_div_doc')
def view_div_doc():
    # Get the list of documents with their corresponding document type and division
    db = get_db()
    documents = db.execute(
        'SELECT d.id, d.name, d.file_path, d.description, dt.name AS docType_name, dv.name AS division_name'
        ' FROM document d'
        ' JOIN docType dt ON d.docType_id = dt.id'
        ' JOIN division_document dd ON d.id = dd.document_id'
        ' JOIN division dv ON dd.division_id = dv.id'
        ' ORDER BY d.name'
    ).fetchall()

    return render_template('admin/view_div_doc.html', documents=documents)


@bp.route('/view_dep_doc')
def view_dep_doc():
    # Get the list of documents with their corresponding document type and Department
    db = get_db()
    documents = db.execute(
        'SELECT d.id, d.name, d.file_path, d.description, dt.name AS docType_name, de.name AS department_name'
        ' FROM document d'
        ' JOIN docType dt ON d.docType_id = dt.id'
        ' JOIN department_document dd ON d.id = dd.document_id'
        ' JOIN department de ON dd.department_id = de.id'
        ' ORDER BY d.name'
    ).fetchall()

    return render_template('admin/view_dep_doc.html', documents=documents)

@bp.route('/view_unit_doc')
def view_unit_doc():
    # Get the list of documents with their corresponding document type and unit
    db = get_db()
    documents = db.execute(
        'SELECT d.id, d.name, d.file_path, d.description, dt.name AS docType_name, u.name AS unit_name'
        ' FROM document d'
        ' JOIN docType dt ON d.docType_id = dt.id'
        ' JOIN unit_document dd ON d.id = dd.document_id'
        ' JOIN unit u ON dd.unit_id = u.id'
        ' ORDER BY d.name'
    ).fetchall()

    return render_template('admin/view_unit_doc.html', documents=documents)
