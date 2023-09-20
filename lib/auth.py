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

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
        g.user = cursor.fetchone()


#logIn
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        password = request.form['password']
        db = get_db()
        error = None

        cursor = db.cursor(dictionary=True)  # Fetch rows as dictionaries
        cursor.execute('SELECT * FROM user WHERE emp_id = %s', (emp_id,))
        user = cursor.fetchone()

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

# Users View 
@bp.route('/view_users')
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def view_users():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM user')

    users =cursor.fetchall()
    return render_template('admin/users.html', users=users)

# Add Users
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
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO user (name, emp_id, email, password, place, position, role_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, emp_id, email, generate_password_hash(password), place, position, role_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {emp_id} is already registered."
            else:
                return redirect(url_for('auth.view_users'))
            flash(error)
    
    return render_template('admin/add_user.html')

# Edit Useres
@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@login_required_role([1])  # '1' is the role_id for the admin role
def edit_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'SELECT id, name, emp_id, email, place, position, role_id FROM user WHERE id = %s',
        (user_id,)
    )
    user = cursor.fetchone()

    if user is None:
        abort(404, f"User id {user_id} doesn't exist.")

    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
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
            cursor.execute(
                'UPDATE user SET name = %s, emp_id = %s, email = %s, place = %s, position = %s, role_id = %s WHERE id = %s',
                (name, emp_id, email, place, position, role_id, user_id)
            )
            db.commit()
            flash('User updated successfully!')
            
            return redirect(url_for('auth.view_users'))

        flash(error)

    return render_template('admin/edit_user.html', user=user)

# delete Users
@bp.route('/delete_user/<int:user_id>', methods=('POST',))
@login_required
@login_required_role([1]) # Only admins can delete users
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT id FROM user WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if user is None:
        abort(404, f"User id {user_id} doesn't exist.")

    cursor.execute('DELETE FROM user WHERE id = %s', (user_id,))
    db.commit()
    flash('User deleted successfully!')
    cursor.close()
    return redirect(url_for('auth.view_users'))

# Reset User Password
@bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def reset_password(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('auth.view_users_req'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('UPDATE user SET password = %s WHERE id = %s', (hashed_password, user_id))
            db.commit()
            #auth.view_users_req_req soon
            flash('Password reset successfully.', 'success')
            return redirect(url_for('auth.view_users_req'))

    return render_template('admin/reset_password.html', user=user)

# Simple User Profile
@bp.route('/profile')
@login_required
def profile():
    # get the current user's profile data from the database
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'SELECT name, emp_id, email, place, position FROM user WHERE emp_id = %s',
        (g.user['emp_id'],)
    )
    user_data = cursor.fetchone()

    return render_template('auth/profile.html', user_data=user_data)


# User Change Password
@bp.route('/change_password', methods=('GET', 'POST'))
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        db = get_db()
        cursor = db.cursor()

        error = None
        cursor.execute(
            'SELECT * FROM user WHERE emp_id = %s', (g.user['emp_id'],)
        )
        user = cursor.fetchone()
        
        # Convert the user tuple into a dictionary
        user_dict = dict(zip([column[0] for column in cursor.description], user))
        
        if not check_password_hash(user_dict['password'], old_password):
            error = 'Incorrect old password'
        elif new_password != confirm_password:
            error = 'Passwords do not match'
        
        if error is None:
            cursor.execute(
                'UPDATE user SET password = %s WHERE emp_id = %s',
                (generate_password_hash(new_password), g.user['emp_id'])
            )
            db.commit()
            flash('Password changed successfully!')
            return redirect(url_for('post.index'))
        
        flash(error)
        cursor.close()
    return render_template('auth/change_password.html')

# To Activate Users 
@bp.route('/activate_user/<int:user_id>', methods=['POST'])
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def activate_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE user SET active = 1 WHERE id = %s', (user_id,))
    db.commit()
    
    return redirect(url_for('auth.view_users'))

# To Deactivate Users 
@bp.route('/deactivate_user/<int:user_id>', methods=['POST'])
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def deactivate_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE user SET active = 0 WHERE id = %s', (user_id,))
    db.commit()
   
    return redirect(url_for('auth.view_users'))

# User request password View 
@bp.route('/view_users_req', methods=['GET'])
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def view_users_req():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM password_reset_request')
    requests = cursor.fetchall()

    return render_template('admin/view_users_req.html', requests=requests)

# User Requesting password Reset
@bp.route('/reset_request', methods=('GET','POST',))
def reset_request():
    emp_id = request.form.get('emp_id')
    email = request.form.get('email')
    reason = request.form.get('reason')

    db = get_db()
    cursor = db.cursor()

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
            cursor.execute(
                'SELECT * FROM user WHERE emp_id = %s',
                (emp_id,)
            )
            user = cursor.fetchone()

            if user is None:
                error = 'Employee ID is not registered!'
            else:
                # Check if a pending request already exists for this employee ID
                cursor.execute(
                    'SELECT * FROM password_reset_request WHERE emp_id = %s AND status = %s',
                    (emp_id, 'pending')
                )
                existing_request = cursor.fetchone()

                if existing_request is not None:
                    error = 'A pending request already exists for this employee ID.'
                    flash(error)
                    return redirect(url_for('auth.login'))
                else:
                    # Insert the password reset request into the table
                    cursor.execute(
                        'INSERT INTO password_reset_request (emp_id, email, reason, status) VALUES (%s, %s, %s, %s)',
                        (emp_id, email, reason, 'pending')
                    )
                    db.commit()
                    flash('Password reset request submitted successfully!')
                    return redirect(url_for('auth.login'))
        except db.IntegrityError:
            error = 'An error occurred while processing your request.'

    return render_template('auth/pass_res_req.html')


@bp.route('/authorize_reset_pass/<int:password_reset_request_id>', methods=['POST'])
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def authorize_reset_pass(password_reset_request_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE password_reset_request SET status = "authorize" WHERE id = %s', (password_reset_request_id,))
    db.commit()

    return redirect(url_for('auth.view_users_req'))


@bp.route('/pending_reset_pass/<int:password_reset_request_id>', methods=['POST'])
@login_required_role([1]) # '1' is the role_id for the admin role
@login_required
def pending_reset_pass(password_reset_request_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE password_reset_request SET status = "pending" WHERE id = %s', (password_reset_request_id,))
    db.commit()
    
    return redirect(url_for('auth.view_users_req'))


@bp.route('/delete_request/<int:request_id>', methods=['POST'])
@login_required_role([1])  # '1' is the role_id for the admin role
@login_required
def delete_request(request_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT id FROM password_reset_request WHERE id = %s', (request_id,))
    request = cursor.fetchone()

    if request is None:
        abort(404, f"Password reset request id {request_id} doesn't exist. ")

    cursor.execute('DELETE FROM password_reset_request WHERE id = %s', (request_id,))
    db.commit()
    flash('Request deleted successfully.', 'success')
    cursor.close()
    return redirect(url_for('auth.view_users_req'))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.route('/unauthorized')
def unauthorized():
    return render_template('auth/unauthorized.html')

#tempo Regist
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        emp_id = request.form['emp_id']
        email = request.form['email']
        password = request.form['password']
        place = request.form['place']
        position = request.form['position']
        role_id = request.form['role_id']

        db = get_db()
        error = None

        if not name:
            error = 'Name is required!'
        elif not emp_id:
            error = 'Employee ID is required!'
        elif not email:
            error = 'Email is required!'
        elif not password:
            error = 'Password is required!'
        elif not place:
            error = 'Place is required!'
        elif not position:
            error = 'Position is required!'
        elif not role_id:
            error = 'Role ID is required!'

        if error is None:
            try:
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO user (name, emp_id, email, password, place, position, role_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, emp_id, email, generate_password_hash(password), place, position, role_id),
                )
                db.commit()
            except Exception as e:
                error = f"User {emp_id} is already registered. Error: {str(e)}"
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


