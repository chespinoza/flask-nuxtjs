import logging
import sys

from app.api.v1 import sensors
from flask import Flask


def create_app(config_object="app.config"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: Configuration object to use.
    """
    # Config
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)

    # Logging
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)

    # Blueprints
    app.register_blueprint(sensors.blueprint)

    return app
