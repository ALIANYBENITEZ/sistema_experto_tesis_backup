from flask import Blueprint

empresas_bp = Blueprint("empresas", __name__, url_prefix="/api/empresas")

from . import routes  # noqa: F401, E402
