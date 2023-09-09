import os
from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='DEV',
        SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:&CorSrvPa&111@localhost/knowlage',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Set up localhost configuration
    app.config['localhost'] = '127.0.0.1'

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    from .db import db, init_app
    db.init_app(app)
    init_app(app)

    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .post import bp as post_bp
    app.register_blueprint(post_bp)

    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from .struc import bp as struc_bp
    app.register_blueprint(struc_bp)

    from .file import bp as file_bp
    app.register_blueprint(file_bp)
    app.add_url_rule('/', endpoint='index')

    # A simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, CBE Staff!'

    return app
