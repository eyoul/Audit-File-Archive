import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='DEV',
        DATABASE={
            'host': 'localhost',
            'user': 'root',
            'password': 'newpassword',
            'database': 'library',
        }
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, CBE Staff!'

    from . import db
    db.init_app(app)

    # Register your blueprints and add URL rules here

    from . import post
    app.register_blueprint(post.bp)
    app.add_url_rule('/', endpoint='index')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import struc
    app.register_blueprint(struc.bp)

    from . import file
    app.register_blueprint(file.bp)

    return app