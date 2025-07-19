from flask import Flask, request, jsonify
from flask_cors import CORS
from jose import jwt
import requests
from os import environ
from functools import wraps

app = Flask(__name__)
CORS(app)
AUTH0_DOMAIN = environ.get("AUTH0_DOMAIN")
API_AUDIENCE = environ.get("API_AUDIENCE")
ALGORITHMS = environ.get("ALGORITHMS", "RS256").split(",")

def verify_jwt(token):
    jsonurl = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = jsonurl.json()
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            break
    
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTClaimsError:
            return None
        except Exception:
            return None

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', "").split("Bearer ")[-1]
        try:
            payload = verify_jwt(token)
        except Exception as e:
            return jsonify({"error": "Unauthorized"}), 401
        return f(payload, *args, **kwargs)
    return decorated

@app.route('/dashboard', methods=['GET']) # TODO: CHANGE THIS TO MATCH WTIH FRONTEND
@requires_auth
def protected_route(payload):
    return jsonify({
        "message": "Access granted!",
        "user": payload
    })

if __name__ == "__main__":
    app.run(debug=True)