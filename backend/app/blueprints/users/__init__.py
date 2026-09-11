from flask import Blueprint

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

from . import routes  # noqa: F401, E402
