import jwt
from flask import request, abort, has_request_context

SECRET_KEY = 'ef860173e6b13b7eec9eaec0dad96d6a3ef3e711'  # sha1('chave_secreta')


def protect(func):
    def wrapper(*args, **kwargs):
        if not has_request_context():
            return abort(401)

        token = request.headers.get('Authorization')
        if not token:
            abort(401)

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.current_user = decoded_token.get('usuario')
        except:
            abort(401)

        return func(*args, **kwargs)

    return wrapper
