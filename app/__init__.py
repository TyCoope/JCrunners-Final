from flask import Flask, g
from .app_factory import create_app
from .db_connect import close_db, get_db
from datetime import timedelta

app = create_app()
app.secret_key = 'your-secret-key'  # Replace with an environment variable

# Register blueprints
from app.blueprints.runners import runners
from app.blueprints.races import races
from app.blueprints.results import results
from app.blueprints.rosters import rosters
from app.blueprints.race_times import race_times

app.register_blueprint(runners)
app.register_blueprint(races)
app.register_blueprint(results)
app.register_blueprint(rosters)
app.register_blueprint(race_times)

# Import routes
from . import routes

@app.before_request
def before_request():
    g.db = get_db()

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)