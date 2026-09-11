from flask import Blueprint

evaluation_bp = Blueprint("evaluation", __name__, url_prefix="/api/evaluations")

from . import routes  # noqa: F401, E402
