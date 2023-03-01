import os
import connexion
from connexion.exceptions import OAuthProblem
from connexion.resolver import MethodViewResolver
import api

options = {'serve_spec': True,
            'swagger_ui': True}

# Some constants
GENERATE_BOLA_ERROR = True
GENERATE_USEAFTERFREE_ERROR = True
GENERATE_500_ERROR = True

TOKEN_DB = {
    'asdf1234567890': {
        'active': True,
        'scope': 'read:pets write:pets',
        'uid': 100
    },
    'test': {
        'active': True,
        'scope': 'read:pets write:pets',
        'uid': 103
    },
    'user1Tok012345': {
        'active': True,
        'scope': 'read:pets',
        'uid': 101
    },
    'user2Tok012345': {
        'active': True,
        'scope': 'read:pets',
        'uid': 102
    }
}

def apikey_auth(token, required_scopes):
    print(f"Receive token '{token}', with required_scopes '{required_scopes}'")
    info = TOKEN_DB.get(token, None)

    if not info:
        raise OAuthProblem('Invalid token')

    return info

def petstore_auth(token, required_scopes):
    return {}

if __name__ == '__main__':
    app = connexion.FlaskApp(__name__)
    app.add_api("petstorev2.json", arguments={'title': 'Petstore V2'}, options=options,
                strict_validation=True, validate_responses=True, resolver_error=501)
    app.run(host='0.0.0.0', port=5000)

