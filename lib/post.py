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