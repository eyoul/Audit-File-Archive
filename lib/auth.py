import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
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
            if user['role_id'] == 1:
                return redirect(url_for('admin.dashboard'))
            elif user['role_id'] == 2:
                return redirect(url_for('post.board'))
            elif user['role_id'] == 3:
                return redirect(url_for('post.board'))
            else:
                error = 'Invalid role.'

        flash(error)

    return render_template('auth/login.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        department= request.form['department']
        position = request.form['position']
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
        elif not department:
            error = 'department required!'
        elif not position:
            error = 'position required!'
        elif not role_id:
            error = 'Role is required!'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, emp_id, email, password, department, position, role_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, emp_id, email, generate_password_hash(password), department, position,  1),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {emp_id} is alrady registerd."
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template('auth/register.html')


@bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        department= request.form['department']
        position = request.form['position']
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
        elif not department:
            error = 'department required!'
        elif not position:
            error = 'position required!'
        elif not role_id:
            error = 'Role is required!'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, emp_id, email, password, department, position, role_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, emp_id, email, generate_password_hash(password), department, position, role_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {emp_id} is already registered."
            else:
                return redirect(url_for('auth.add_user'))
            flash(error)
    
    return render_template('admin/add_user.html')


@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    db = get_db()
    user = db.execute(
        'SELECT id, name, emp_id, email, department, position, role_id FROM user WHERE id = ?',
        (user_id,)
    ).fetchone()

    if user is None:
        abort(404, f"User id {user_id} doesn't exist.")

    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        department= request.form['department']
        position = request.form['position']
        role_id = request.form['role_id']
        error = None

        if not name:
            error = 'Name is required!'
        elif not emp_id:
            error = 'Employee Id required!'
        elif not email:
            error = 'Email required!'
        elif not department:
            error = 'department required!'
        elif not position:
            error = 'position required!'
        elif not role_id:
            error = 'Role is required!'

        if error is None:
            db.execute(
                'UPDATE user SET name = ?, emp_id = ?, email = ?, password = ?, department = ?, position = ?, role_id = ? WHERE id = ?',
                (name, emp_id, email, generate_password_hash(password), department, position, role_id, user_id)
            )
            db.commit()
            flash('User updated successfully!')
            return redirect(url_for('auth.add_user'))

        flash(error)

    return render_template('admin/edit_user.html', user=user)

@bp.route('/view_users')
def view_users():
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('admin/users.html', users=users)


@bp.route('/delete_user/<int:user_id>', methods=('POST',))
@login_required_role(1) # Only admins can delete users
def delete_user(user_id):
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.commit()
    flash('User deleted successfully!')
    return redirect(url_for('auth.view_users'))


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

@bp.route('/unauthorized')
def unauthorized():
    return render_template('auth/unauthorized.html')
