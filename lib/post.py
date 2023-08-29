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

# index file 
@bp.route('/')
@login_required
def index():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT id, name, description FROM division')
    divisions = cursor.fetchall()

    cursor.execute('SELECT id, name, description, division_id FROM department')
    departments = cursor.fetchall()

    cursor.execute('SELECT id, name, description, department_id FROM unit')
    units = cursor.fetchall()

    cursor.execute('SELECT id, name, file_path, description, docType_id, division_id, department_id, unit_id FROM document')
    documents = cursor.fetchall()

    cursor.execute('SELECT id, name, period, description, division_id, department_id, unit_id FROM audit_program')
    programs = cursor.fetchall()

    cursor.execute('''
        SELECT audit_File.*, audit_File_Type.name AS type_name
        FROM audit_File
        JOIN audit_File_Type ON audit_File.file_type_id = audit_File_Type.id
        ORDER BY audit_File.name
    ''')
    audit_files = cursor.fetchall()

    cursor.close()

    return render_template('post/index.html', divisions=divisions, departments=departments,
                           units=units, documents=documents, programs=programs, audit_files=audit_files)


@bp.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@bp.route('/docType')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def docType():
    db = get_db()
    docTypes = db.execute(
        'SELECT id, name, description FROM docType ORDER BY name'
    ).fetchall()
    return render_template('admin/docTypes.html', docTypes=docTypes)


@bp.route('/add_doc_type', methods=['GET', 'POST'])
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_doc_type(doc_type_id):
    db = get_db()
    db.execute('DELETE FROM docType WHERE id = ?', (doc_type_id,))
    db.commit()
    flash('Document type deleted successfully!')
    return redirect(url_for('post.docType'))


@bp.route('/view_div_doc')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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


@bp.route('/add_div_file', methods=('GET', 'POST'))
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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
            return redirect(url_for('post.view_div_doc'))

    return render_template('admin/add_div_file.html', docTypes=docTypes, 
                           divisions=divisions)


@bp.route('/edit_div_file/<int:doc_id>', methods=('GET', 'POST'))
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def edit_div_file(doc_id):
    db = get_db()
    document = db.execute(
        'SELECT * FROM document WHERE id = ?', (doc_id,)
    ).fetchone()

    # Get the list of document types to populate the select element
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
        if 'file_path' in request.files:
            file = request.files['file_path']
            if file.filename != '':
                if not allowed_file(file.filename):
                    error = 'Invalid file type. Only Pdf, Doc, Docx, Xls, Xlsx, Csv, and Rtf are allowed.'
                else:
                    # Save the new file
                    filename = secure_filename(file.filename)
                    _, ext = os.path.splitext(filename)
                    # Generate a unique filename using uuid4()
                    unique_filename = str(uuid.uuid4()) + ext
                    file.save(os.path.join(UPLOAD_FOLDER, unique_filename))

                    # Delete the old file
                    if document['file_path'] is not None:
                        os.remove(os.path.join(UPLOAD_FOLDER, document['file_path']))

                    # Update the file path in the database
                    db.execute(
                        'UPDATE document SET file_path = ? WHERE id = ?',
                        (unique_filename, doc_id)
                    )
                    db.commit()

        # Update the document record if there are no errors
        if error is None:
            db.execute(
                'UPDATE document SET name = ?, description = ?, docType_id = ?, division_id = ?'
                ' WHERE id = ?',
                (name, description, docType_id, division_id, doc_id)
            )
            db.commit()
            flash('Document updated successfully!')
            return redirect(url_for('post.view_div_doc'))

        flash(error)

    return render_template('admin/edit_div_file.html', document=document, docTypes=docTypes, 
                           divisions=divisions)


@bp.route('/delete_div_file/<int:id>', methods=('POST',))
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_div_file(id):
    db = get_db()
    document = db.execute(
        'SELECT id, file_path FROM document WHERE id = ?',
        (id,)
    ).fetchone()

    if document is None:
        abort(404, f"Document id {id} doesn't exist.")

    # Delete the document file from the server
    os.remove(os.path.join(UPLOAD_FOLDER, document['file_path']))

    db.execute('DELETE FROM document WHERE id = ?', (id,))
    db.execute('DELETE FROM division_document WHERE document_id = ?', (id,))
    db.commit()
    flash('File deleted successfully!')
    return redirect(url_for('post.view_div_doc'))


@bp.route('/view_dep_doc')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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


@bp.route('/add_dep_file', methods=('GET', 'POST'))
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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
            return redirect(url_for('post.view_dep_doc'))

    return render_template('admin/add_dep_file.html', docTypes=docTypes, 
                            departments=departments)

@bp.route('/edit_dep_file/<int:doc_id>', methods=('GET', 'POST'))
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def edit_dep_file(doc_id):
    db = get_db()
    document = db.execute(
        'SELECT d.id, d.name, d.file_path, d.description, d.docType_id, d.department_id'
        ' FROM document d JOIN department_document dd ON d.id = dd.document_id'
        ' WHERE d.id = ?',
        (doc_id,)
    ).fetchone()

    if document is None:
        flash('Document does not exist.')
        return redirect(url_for('post.view_dep_doc'))

    # Get the list of document types to populate the select element
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
        if 'file_path' in request.files:
            file = request.files['file_path']
            if file.filename != '' and not allowed_file(file.filename):
                error = 'Invalid file type. Only Pdf, Doc, Docx, Xls, Xlsx, Csv, and Rtf are allowed.'

        # Handle errors and success
        if error is not None: 
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            # Update the document in the document table
            if 'file_path' in request.files and file.filename != '':
                filename = secure_filename(file.filename)
                _, ext = os.path.splitext(filename)
                # Generate a unique filename using uuid4()
                unique_filename = str(uuid.uuid4()) + ext
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                cursor.execute(
                    'UPDATE document SET name=?, file_path=?, description=?, docType_id=?, department_id=? WHERE id=?',
                    (name, unique_filename, description, docType_id, department_id, doc_id)
                )
            else:
                cursor.execute(
                    'UPDATE document SET name=?, description=?, docType_id=?, department_id=? WHERE id=?',
                    (name, description, docType_id, department_id, doc_id)
                )

            # Update the department-document mapping in the department_document table
            cursor.execute(
                'UPDATE department_document SET department_id=? WHERE document_id=?',
                (department_id, doc_id)
            )

            db.commit()
            flash('Document updated successfully!')
            return redirect(url_for('post.view_dep_doc'))

    return render_template('admin/edit_dep_file.html', document=document, docTypes=docTypes, departments=departments)


@bp.route('/delete_dep_file/<int:id>', methods=('POST',))
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_dep_file(id):
    db = get_db()
    document = db.execute(
        'SELECT id, file_path FROM document WHERE id = ?',
        (id,)
    ).fetchone()

    if document is None:
        abort(404, f"Document id {id} doesn't exist.")

    # Delete the document file from the server
    os.remove(os.path.join(UPLOAD_FOLDER, document['file_path']))

    db.execute('DELETE FROM document WHERE id = ?', (id,))
    db.execute('DELETE FROM department_document WHERE document_id = ?', (id,))
    db.commit()
    flash('File deleted successfully!')
    return redirect(url_for('post.view_dep_doc'))

@bp.route('/view_unit_doc')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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


@bp.route('/add_unit_file', methods=('GET', 'POST'))
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
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
            return redirect(url_for('post.view_unit_doc'))

    return render_template('admin/add_unit_file.html', docTypes=docTypes, units=units)

@bp.route('/delete_unit_file/<int:id>', methods=('POST',))
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_unit_file(id):
    db = get_db()
    document = db.execute(
        'SELECT id, file_path FROM document WHERE id = ?',
        (id,)
    ).fetchone()

    if document is None:
        abort(404, f"Document id {id} doesn't exist.")

    # Delete the document file from the server
    os.remove(os.path.join(UPLOAD_FOLDER, document['file_path']))

    db.execute('DELETE FROM document WHERE id = ?', (id,))
    db.execute('DELETE FROM unit_document WHERE document_id = ?', (id,))
    db.commit()
    flash('File deleted successfully!')
    return redirect(url_for('post.view_unit_doc'))


@bp.route('/edit_unit_file/<int:doc_id>', methods=('GET', 'POST'))
@login_required_role([1, 2])  # '1' is the role_id for the admin role
@login_required
def edit_unit_file(doc_id):
    db = get_db()
    document = db.execute(
        'SELECT u.id, u.name, u.file_path, u.description, u.docType_id, u.unit_id'
        ' FROM document u JOIN unit_document dd ON u.id = dd.document_id'
        ' WHERE u.id = ?',
        (doc_id,)
    ).fetchone()

    if document is None:
        flash('Document does not exist.')
        return redirect(url_for('post.view_unit_doc'))

    # Get the list of document types to populate the select element
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
        if 'file_path' in request.files:
            file = request.files['file_path']
            if file.filename != '' and not allowed_file(file.filename):
                error = 'Invalid file type. Only Pdf, Doc, Docx, Xls, Xlsx, Csv, and Rtf are allowed.'

        # Handle errors and success
        if error is not None: 
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            # Update the document in the document table
            if 'file_path' in request.files and file.filename != '':
                filename = secure_filename(file.filename)
                _, ext = os.path.splitext(filename)
                # Generate a unique filename using uuid4()
                unique_filename = str(uuid.uuid4()) + ext
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                cursor.execute(
                    'UPDATE document SET name=?, file_path=?, description=?, docType_id=?, unit_id=? WHERE id=?',
                    (name, unique_filename, description, docType_id, unit_id, doc_id)
                )
            else:
                cursor.execute(
                    'UPDATE document SET name=?, description=?, docType_id=?, unit_id=? WHERE id=?',
                    (name, description, docType_id, unit_id, doc_id)
                )

            # Update the unit-document mapping in the unit_document table
            cursor.execute(
                'UPDATE unit_document SET unit_id=? WHERE document_id=?',
                (unit_id, doc_id)
            )

            db.commit()
            flash('Document updated successfully!')
            return redirect(url_for('post.view_dep_doc'))

    return render_template('admin/edit_unit_file.html', document=document, docTypes=docTypes, units=units)

@bp.route('/search')
def search():
    query = request.args.get('q')
    db = get_db()

    div = db.execute(
    'SELECT * FROM division WHERE name LIKE ?',
    ('%' + query + '%',)
    ).fetchall()

    dep = db.execute(
        'SELECT * FROM department WHERE name LIKE ?',
        ('%' + query + '%',)
    ).fetchall()

    unit = db.execute(
        'SELECT * FROM unit WHERE name LIKE ?',
        ('%' + query + '%',)
    ).fetchall()

    documents = db.execute(
        'SELECT * FROM document WHERE name LIKE ?',
        ('%' + query + '%',)
    ).fetchall()

    auditprogram = db.execute(
        'SELECT * FROM audit_program WHERE name LIKE ?',
        ('%' + query + '%',)
    ).fetchall()

    auditfiles = db.execute(
        'SELECT * FROM audit_File WHERE name LIKE ?',
        ('%' + query + '%',)
    ).fetchall()

    return render_template('post/search.html', documents=documents, auditfiles=auditfiles, div=div,
                           dep=dep, unit=unit, auditprogram=auditprogram, query=query)
