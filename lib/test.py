
@bp.route('/create', methods=('GET', 'POST'))
def create():
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
            error = 'Document  Type  is required.'
        elif not :
            error = 'Location is required.'
        
        # Handle photo_url upload
        if 'file_path' not in request.files:
            error = 'Photo is required.'
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
            return redirect(url_for('blog.index'))

    return render_template('admin/add_file.html')



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
                'INSERT INTO document (name, file_path, description, docType_id)'
                ' VALUES (?, ?, ?, ?)',
                (name, unique_filename, description, docType_id)
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

    return render_template('admin/add_file.html', docTypes=docTypes, 
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
                'INSERT INTO document (name, file_path, description, docType_id)'
                ' VALUES (?, ?, ?, ?)',
                (name, unique_filename, description, docType_id)
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

    return render_template('admin/add_file.html', docTypes=docTypes, 
                            departments=departments)




@bp.route('/add_file', methods=('GET', 'POST'))
def add_file():
    # Get the list of document types to populate the select element
    db = get_db()
    docTypes = db.execute(
        'SELECT id, name FROM docType ORDER BY name'
    ).fetchall()

    # Get the list of divisions to populate the select element
    divisions = db.execute(
        'SELECT id, name FROM division ORDER BY name'
    ).fetchall()

    # Get the list of departments to populate the select element
    departments = db.execute(
        'SELECT id, name FROM department ORDER BY name'
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
        division_id = request.form['division_id']
        department_id = request.form['department_id']
        unit_id = request.form['unit_id']

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
        elif not department_id:
            error = 'Department is required.'
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
                'INSERT INTO document (name, file_path, description, docType_id)'
                ' VALUES (?, ?, ?, ?)',
                (name, unique_filename, description, docType_id)
            )

            doc_id = cursor.lastrowid

            # Insert the document into the division_document table
            cursor.execute(
                'INSERT INTO division_document (division_id, document_id)'
                ' VALUES (?, ?)',
                (division_id, doc_id)
            )

            # Insert the document into the department_document table
            cursor.execute(
                'INSERT INTO department_document (department_id, document_id)'
                ' VALUES (?, ?)',
                (department_id, doc_id)
            )

            # Insert the document into the unit_document table
            cursor.execute(
                'INSERT INTO unit_document (unit_id, document_id)'
                ' VALUES (?, ?)',
                (unit_id, doc_id)
            )

            db.commit()
            flash('File added successfully!')
            return redirect(url_for('post.add_file'))

    return render_template('admin/add_file.html', docTypes=docTypes, 
                           divisions=divisions, departments=departments, units=units)