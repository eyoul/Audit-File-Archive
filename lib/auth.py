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


def login_required_role(role_list):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            if g.user['role_id'] not in role_list:
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
        elif not user['active']:
            error = 'User account is inactive.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('post.index'))
        flash(error)

    return render_template('auth/login.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        place= request.form['place']
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
        elif not place:
            error = 'place required!'
        elif not position:
            error = 'position required!'
        elif not role_id:
            error = 'Role is required!'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, emp_id, email, password, place, position, role_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, emp_id, email, generate_password_hash(password), place, position,  1),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {emp_id} is alrady registerd."
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template('auth/register.html')


@bp.route('/view_users')
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def view_users():
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('admin/users.html', users=users)

@bp.route('/add_user', methods=['GET', 'POST'])
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        place= request.form['place']
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
        elif not place:
            error = 'place required!'
        elif not position:
            error = 'position required!'
        elif not role_id:
            error = 'Role is required!'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, emp_id, email, password, place, position, role_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, emp_id, email, generate_password_hash(password), place, position, role_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {emp_id} is already registered."
            else:
                return redirect(url_for('auth.view_users'))
            flash(error)
    
    return render_template('admin/add_user.html')


@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@login_required_role([1])  # '1' is the role_id for the admin role
def edit_user(user_id):
    db = get_db()
    user = db.execute(
        'SELECT id, name, emp_id, email, place, position, role_id FROM user WHERE id = ?',
        (user_id,)
    ).fetchone()

    if user is None:
        abort(404, f"User id {user_id} doesn't exist.")

    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        place= request.form['place']
        position = request.form['position']
        role_id = request.form['role_id']
        error = None

        if not name:
            error = 'Name is required!'
        elif not emp_id:
            error = 'Employee Id required!'
        elif not email:
            error = 'Email required!'
        elif not place:
            error = 'place required!'
        elif not position:
            error = 'position required!'
        elif not role_id:
            error = 'Role is required!'

        if error is None:
            db.execute(
                'UPDATE user SET name = ?, emp_id = ?, email = ?, password = ?, place = ?, position = ?, role_id = ? WHERE id = ?',
                (name, emp_id, email, generate_password_hash(password), place, position, role_id, user_id)
            )
            db.commit()
            flash('User updated successfully!')
            return redirect(url_for('auth.view_users'))

        flash(error)

    return render_template('admin/edit_user.html', user=user)


@bp.route('/profile')
@login_required
def profile():
    # get the current user's profile data from the database
    db = get_db()
    user_data = db.execute(
        'SELECT name, emp_id, email, place, position FROM user WHERE emp_id = ?',
        (g.user['emp_id'],)
    ).fetchone()
    return render_template('auth/profile.html', user_data=user_data)


@bp.route('/change_password', methods=('GET', 'POST'))
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE emp_id = ?', (g.user['emp_id'],)
        ).fetchone()
        
        if not check_password_hash(user['password'], old_password):
            error = 'Incorrect old password'
        elif new_password != confirm_password:
            error = 'Passwords do not match'
        
        if error is None:
            db.execute(
                'UPDATE user SET password = ? WHERE emp_id = ?',
                (generate_password_hash(new_password), g.user['emp_id'])
            )
            db.commit()
            flash('Password changed successfully!')
            return redirect(url_for('post.index'))
        
        flash(error)
    
    return render_template('auth/change_password.html')


@bp.route('/delete_user/<int:user_id>', methods=('POST',))
@login_required
@login_required_role([1]) # Only admins can delete users
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


@bp.route('/activate_user/<int:user_id>', methods=['POST'])
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def activate_user(user_id):
    db = get_db()
    db.execute('UPDATE user SET active = 1 WHERE id = ?', (user_id,))
    db.commit()
    return redirect(url_for('auth.view_users'))


@bp.route('/deactivate_user/<int:user_id>', methods=['POST'])
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def deactivate_user(user_id):
    db = get_db()
    db.execute('UPDATE user SET active = 0 WHERE id = ?', (user_id,))
    db.commit()
    return redirect(url_for('auth.view_users'))


@bp.route('/reset_request', methods=('GET','POST',))
def reset_request():
    emp_id = request.form.get('emp_id')
    email = request.form.get('email')
    reason = request.form.get('reason')

    db = get_db()
    error = None

    if not emp_id:
        error = 'Employee ID is required!'
    elif not email:
        error = 'Email is required!'
    elif not reason:
        error = 'Reason is required!'

    if error is None:
        try:
            # Check if the employee ID exists in the user table
            user = db.execute(
                'SELECT * FROM user WHERE emp_id = ?',
                (emp_id,)
            ).fetchone()

            if user is None:
                error = 'Employee ID is not registered!'
            else:
                # Check if a pending request already exists for this employee ID
                existing_request = db.execute(
                    'SELECT * FROM password_reset_request WHERE emp_id = ? AND status = ?',
                    (emp_id, 'pending')
                ).fetchone()

                if existing_request is not None:
                    error = 'A pending request already exists for this employee ID.'
                    flash(error)
                    return redirect(url_for('auth.login'))
                else:
                    # Insert the password reset request into the table
                    db.execute(
                        'INSERT INTO password_reset_request (emp_id, email, reason, status) VALUES (?, ?, ?, ?)',
                        (emp_id, email, reason, 'pending')
                    )
                    db.commit()
                    flash('Password reset request submitted successfully!')
                    return redirect(url_for('auth.login'))
        except db.IntegrityError:
            error = 'An error occurred while processing your request.'

    return render_template('auth/pass_res_req.html')
