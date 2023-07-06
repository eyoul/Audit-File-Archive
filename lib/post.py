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

#Upload file path
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'lib', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'rtf' }

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

bp = Blueprint('post', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    return render_template('post/index.html')

@bp.route('/board')
def board():
    return render_template('post/board.html')


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



@bp.route('/add_file', methods=('GET', 'POST'))
def add_file():
    # Get the list of document types to populate the select element
    db = get_db()
    docTypes = db.execute(
        'SELECT id, name FROM docType ORDER BY name'
    ).fetchall()

    # Handle form submission
    if request.method == 'POST':
        # Extract form inputs
        name = request.form['name'].upper()
        description = request.form['description']
        docType_id = request.form['docType_id']     

        error = None

        # Validate form inputs
        if not name:
            error = 'Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not docType_id:
            error = 'Document Type is required.'
        
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
            db.execute(
                'INSERT INTO document (name, file_path, description, docType_id)'
                ' VALUES (?, ?, ?, ?)',
                (name, unique_filename, description, docType_id)
            )
            db.commit()
            flash('File added successfully!')
            return redirect(url_for('post.add_file'))

    return render_template('admin/add_file.html', docTypes=docTypes)