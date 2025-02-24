from flask import jsonify


def success_response(message, data=None, status_code=200):
    response = {
        'status': 'success',
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


def error_response(message, errors=None, status_code=400):
    response = {
        'status': 'error',
        'message': message,
        'errors': errors
    }
    return jsonify(response), status_code


def validation_error_response(errors, message='Validation failed', status_code=422):
    response = {
        'status': 'fail',
        'message': message,
        'errors': errors
    }
    return jsonify(response), status_code