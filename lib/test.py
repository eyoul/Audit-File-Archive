
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