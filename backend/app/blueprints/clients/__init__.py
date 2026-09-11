from flask import Blueprint

clients_bp = Blueprint("clients", __name__, url_prefix="/api/clients")

from . import routes  # noqa: F401, E402
