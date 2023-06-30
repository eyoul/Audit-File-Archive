import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from lib.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view 


def login_required_role(role_id):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            if g.user['role_id'] != role_id:
                return redirect(url_for('auth.unauthorized'))

            return f(*args, **kwargs)
        return wrapped_view
    return decorator


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE emp_id = ?', (emp_id,)
        ).fetchone()

        if user is None:
            error = 'Incorrect emp_id.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form['role_id']

        db = get_db()
        error = None

        if not name:
            error = 'Name is required!'
        elif not emp_id:
            error = 'Employee Id required!'
        elif not email:
            error = 'Email required!'
        elif not password:
            error = 'Password required!'
        elif not role_id:
            error = 'Role is required!'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, emp_id, email, password, role_id) VALUES (?, ?, ?, ?, ?)",
                    (name, emp_id, email, generate_password_hash(password), 1),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {emp_id} is alrady registerd."
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template('auth/register.html')

"""
@bp.route('/add_user', method=('GET', 'POST'))
@login_required_role(1)
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form['role_id']

        db = get_db()
        error = None

        if not name:
            error = 'Name is required!'
        elif not emp_id:
            error = 'Employee Id required!'
        elif not email:
            error = 'Email required!'
        elif not password:
            error = 'Password required!'
        elif not role_id:
            error = 'Role is required!'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, emp_id, email, password, role_id) VALUES (?, ?, ?, ?, ?)",
                    (name, emp_id, email, generate_password_hash(password), role_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {emp_id} is already registered."
            else:
                return redirect(url_for('auth.add_user'))
            flash(error)
    
    return render_template('auth/add_user.html')
"""
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)

        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))