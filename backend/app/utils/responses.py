from flask import jsonify


def success(data=None, message="OK", status=200):
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status


def error(message="Error", status=400, details=None):
    response = {"success": False, "message": message}
    if details:
        response["details"] = details
    return jsonify(response), status
