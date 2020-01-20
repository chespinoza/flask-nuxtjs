import json
from functools import wraps
from http import HTTPStatus
from urllib.request import urlopen

from app import config
from flask import _request_ctx_stack, request
from jose import jwt


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            {
                "code": "authorization_header_missing",
                "description": "Authorization header is expected.",
            },
            HTTPStatus.UNAUTHORIZED,
        )

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": 'Authorization header must start with "Bearer".',
            },
            HTTPStatus.UNAUTHORIZED,
        )

    elif len(parts) == 1:
        raise AuthError(
            {"code": "invalid_header", "description": "Token not found."},
            HTTPStatus.UNAUTHORIZED,
        )

    elif len(parts) > 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must be bearer token.",
            },
            HTTPStatus.UNAUTHORIZED,
        )

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen(f"https://{config.AUTH0_DOMAIN}/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=config.ALGORITHMS,
                    audience=config.API_AUDIENCE,
                    issuer="https://" + config.AUTH0_DOMAIN + "/",
                )

            except jwt.ExpiredSignatureError:
                raise AuthError(
                    {"code": "token_expired", "description": "Token expired."},
                    HTTPStatus.UNAUTHORIZED,
                )

            except jwt.JWTClaimsError:
                raise AuthError(
                    {
                        "code": "invalid_claims",
                        "description": "Incorrect claims. Please, check the audience and issuer.",
                    },
                    HTTPStatus.UNAUTHORIZED,
                )
            except Exception:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Unable to parse authentication token.",
                    },
                    HTTPStatus.BAD_REQUEST,
                )

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)

        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Unable to find the appropriate key.",
            },
            HTTPStatus.BAD_REQUEST,
        )

    return decorated
