import contextlib
import logging

from flask import Blueprint, render_template

from app.db.connection import current_local
from app.services.sample_service import select_latest_sample_for_all


logger = logging.getLogger(__name__)
dashboard_ns = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_ns.route("/")
def index():
    with contextlib.closing(current_local.connection.cursor()) as cursor:
        greenhouses = select_latest_sample_for_all(cursor)
    return render_template(
        "index.html",
        greenhouses=greenhouses
    )
