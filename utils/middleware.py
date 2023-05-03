# /utils/middleware.py
import jwt
from flask import request, g, has_request_context, jsonify
from functools import wraps

from models import Usuario, Session

SECRET_KEY = 'ef860173e6b13b7eec9eaec0dad96d6a3ef3e711'  # sha1('chave_secreta')

# Substitua isso pelo ID do usuário que deseja autorizar automaticamente para requisições originadas da tela de documentação
AUTHORIZED_USER_ID = 1

# Substitua isso pela URL da tela de documentação
DOCUMENTATION_URL = ['http://127.0.0.1:5000/openapi/swagger', 'http://127.0.0.1:5000/openapi/swagger']


def protect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not has_request_context():
            return jsonify({'message': 'Request context is missing'}), 401
        token = request.headers.get('Authorization')

        # Verifica se a requisição é originária da tela de documentação
        if request.headers.get('Referer') in DOCUMENTATION_URL:
            session = Session()
            usuario = session.query(Usuario).filter(Usuario.id == AUTHORIZED_USER_ID).first()
            g.current_user = usuario
        else:
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
                return jsonify({'message': f'Invalid token {e}'}), 401
        return func(*args, **kwargs)

    return wrapper
