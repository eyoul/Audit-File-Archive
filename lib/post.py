from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lib.auth import login_required
from lib.db import get_db

bp = Blueprint('post', __name__)



@bp.route('/')
def index():
    return render_template('post/index.html')

@bp.route('/board')
def board():
    return render_template('post/board.html')


@bp.route('/doc_types')
def doc_types():
    db = get_db()
    doc_types = db.execute(
        'SELECT id, name, description FROM docType ORDER BY name'
    ).fetchall()
    return render_template('admin/doc_types.html', doc_types=doc_types)


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
            return redirect(url_for('post.doc_types'))

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
            return redirect(url_for('post.doc_types'))

        flash(error)

    return render_template('admin/edit_doc_type.html', doc_type=doc_type)

@bp.route('/delete_doc_type/<int:doc_type_id>', methods=['POST'])
def delete_doc_type(doc_type_id):
    db = get_db()
    db.execute('DELETE FROM docType WHERE id = ?', (doc_type_id,))
    db.commit()
    flash('Document type deleted successfully!')
    return redirect(url_for('post.doc_types'))