# /utils/middleware.py
import jwt
from flask import request, g, has_request_context, jsonify
from functools import wraps

from models import Usuario, Session

SECRET_KEY = 'ef860173e6b13b7eec9eaec0dad96d6a3ef3e711'  # sha1('chave_secreta')


def protect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not has_request_context():
            return jsonify({'message': 'Request context is missing'}), 401
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.replace('Bearer ', '')
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('sub')
            session = Session()
            usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
            g.current_user = usuario
        except Exception as e:
            return jsonify({'message': 'Invalid token'}), 401
        return func(*args, **kwargs)

    return wrapper
