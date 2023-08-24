import mysql.connector
import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='newpassword',
            database='library',
            autocommit=True
        )
        g.db.row_factory = mysql.connector.cursor.MySQLCursorDict

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        cursor = db.cursor()
        cursor.execute(f.read().decode('utf8'))

    cursor.close()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
