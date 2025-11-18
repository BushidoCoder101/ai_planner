import sqlite3
import click
import os
import json
from flask import current_app, g

def get_db():
    """Connect to the application's configured database. The connection is unique for each request and will be reused if this is called again."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """If this request connected to the database, close the connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    # schema.sql is in the same directory as this db.py file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        db.executescript(f.read())

@click.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app. This is called by the application factory."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# --- Ideas CRUD ---

def create_idea(goal):
    db = get_db()
    cursor = db.execute("INSERT INTO ideas (goal) VALUES (?)", (goal,))
    db.commit()
    return get_idea(cursor.lastrowid)

def get_idea(id):
    return get_db().execute("SELECT * FROM ideas WHERE id = ?", (id,)).fetchone()

def get_ideas():
    return get_db().execute("SELECT id, goal FROM ideas ORDER BY id DESC").fetchall()

def update_idea(id, goal):
    db = get_db()
    db.execute("UPDATE ideas SET goal = ? WHERE id = ?", (goal, id))
    db.commit()
    return get_idea(id)

def delete_idea(id):
    get_db().execute("DELETE FROM ideas WHERE id = ?", (id,))
    get_db().commit()

# --- Missions CRUD ---

def create_mission(mission):
    db = get_db()
    db.execute(
        "INSERT INTO missions (id, goal, status) VALUES (?, ?, ?)",
        (mission.id, mission.goal, mission.status.value)
    )
    db.commit()

def get_all_missions():
    return get_db().execute("SELECT * FROM missions ORDER BY id DESC").fetchall()

def update_mission_state(mission):
    """Updates a mission's status, plan, report, etc."""
    db = get_db()
    db.execute(
        """UPDATE missions SET status = ?, plan = ?, report = ?, clarified_goal = ?
           WHERE id = ?""",
        (mission.status.value, json.dumps(mission.plan), mission.report, mission.clarified_goal, mission.id)
    )
    db.commit()

def delete_mission(id):
    get_db().execute("DELETE FROM missions WHERE id = ?", (id,))
    get_db().commit()