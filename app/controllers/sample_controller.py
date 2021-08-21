import contextlib
import logging
from dataclasses import asdict

from flask import Blueprint, request, abort

from app.db.connection import current_local
from app.services.sample_service import insert_sample, select_latest_sample_for_serial

logger = logging.getLogger(__name__)
sample_ns = Blueprint("greenhouse", __name__, url_prefix="/greenhouse")


SUCCESS_MESSAGE = "OK"


def prepare_message_response(message=SUCCESS_MESSAGE):
    return {
        "message": message
    }


@sample_ns.route("/<serial>/sample", methods=["POST"])
def create_sample(serial):
    with contextlib.closing(current_local.connection.cursor()) as cursor:
        try:
            insert_sample(cursor, serial=serial, **request.json)
        except TypeError:
            logger.exception("Invalid request.")
            return abort(400)
    return prepare_message_response()


@sample_ns.route("/<serial>/sample/latest", methods=["GET"])
def get_latest_sample(serial):
    with contextlib.closing(current_local.connection.cursor()) as cursor:
        sample = select_latest_sample_for_serial(cursor, serial)
    if not sample:
        return abort(404)
    return asdict(sample)
