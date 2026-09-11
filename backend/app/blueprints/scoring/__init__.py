from flask import Blueprint

scoring_bp = Blueprint("scoring", __name__, url_prefix="/api/scoring")

from . import routes  # noqa: F401, E402
