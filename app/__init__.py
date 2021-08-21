import contextlib
from flask import Flask

from app.controllers import dashboard_ns, sample_ns
from app.db.connection import current_local, initialize_tables


def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app.register_blueprint(dashboard_ns)
    app.register_blueprint(sample_ns)
    with app.app_context():
        with contextlib.closing(current_local.connection) as connection:
            initialize_tables(connection)
    return app
