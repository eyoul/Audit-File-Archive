import click
from flask import current_app, g
import mysql.connector

def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB']
            )
            g.db.row_factory = mysql.connector.cursor.MySQLCursorDict
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        try:
            db.close()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        try:
            cursor = db.cursor()
            cursor.execute(f.read().decode('utf8'))
            cursor.close()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    try:
        init_db()
        click.echo('Initialized the database.')
    except Exception as e:
        print(f"An error occurred: {e}")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
