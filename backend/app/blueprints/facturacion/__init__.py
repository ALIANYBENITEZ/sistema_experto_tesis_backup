from flask import Blueprint

facturacion_bp = Blueprint("facturacion", __name__, url_prefix="/api/facturacion")

from . import routes  # noqa: F401, E402
