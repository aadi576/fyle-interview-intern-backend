import json
from flask import request, jsonify
from core.libs import assertions
from functools import wraps

class AuthPrincipal:
    def __init__(self, user_id, student_id=None, teacher_id=None, principal_id=None):
        self.user_id = user_id
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.principal_id = principal_id

def accept_payload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            incoming_payload = request.json
        except Exception as e:
            return jsonify({'error': 'Invalid JSON payload', 'message': str(e)}), 400
        return func(incoming_payload, *args, **kwargs)
    return wrapper

def authenticate_principal(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        p_str = request.headers.get('X-Principal')
        if p_str is None:
            return jsonify({'error': 'Principal not found'}), 401

        try:
            p_dict = json.loads(p_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid principal data'}), 400

        # Extracting principal data safely
        user_id = p_dict.get('user_id')
        student_id = p_dict.get('student_id')
        teacher_id = p_dict.get('teacher_id')
        principal_id = p_dict.get('principal_id')

        p = AuthPrincipal(
            user_id=user_id,
            student_id=student_id,
            teacher_id=teacher_id,
            principal_id=principal_id
        )

        # Validate principal based on path
        path = request.path
        if path.startswith('/student'):
            if p.student_id is None:
                return jsonify({'error': 'Requester should be a student'}), 403
        elif path.startswith('/teacher'):
            if p.teacher_id is None:
                return jsonify({'error': 'Requester should be a teacher'}), 403
        elif path.startswith('/principal'):
            if p.principal_id is None:
                return jsonify({'error': 'Requester should be a principal'}), 403
        else:
            return jsonify({'error': 'No such API'}), 404

        return func(p, *args, **kwargs)
    return wrapper
