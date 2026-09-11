from flask import Blueprint

auditoria_bp = Blueprint("auditoria", __name__, url_prefix="/api/auditoria")

from . import routes  # noqa: F401, E402
