from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'message': 'Bad Request',
            'details': str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized',
            'details': str(error)
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'status': 'error',
            'message': 'Forbidden',
            'details': str(error)
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Not Found',
            'details': str(error)
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal Server Error',
            'details': str(error)
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({
                'status': 'error',
                'message': e.name,
                'details': e.description
            }), e.code
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'details': str(e)
        }), 500