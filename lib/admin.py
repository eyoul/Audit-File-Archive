import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from lib.auth import login_required_role
from lib.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required_role([1, 2])  # '1' is the role_id for the admin role
def dashboard():
    return render_template('admin/dashboard.html')

"""
confidentailaty requirement 
    pesronal 
    on unit or department
    on division 
"""