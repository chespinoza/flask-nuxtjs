import random

from app.api.common import auth
from flask import Blueprint, jsonify

blueprint = Blueprint("sensors", __name__, url_prefix="/api/v1/sensors")


@blueprint.route("/", methods=["GET"])
def sensors_root():
    return jsonify(mesg="Public Access")


@blueprint.route("/data", methods=["GET"])
@auth.requires_auth
def sensors_data():
    return jsonify(label=int(10 * random()), value=random())


@blueprint.errorhandler(auth.AuthError)
def handle_auth_error(exc):
    response = jsonify(exc.error)
    response.status_code = exc.status_code
    return response
