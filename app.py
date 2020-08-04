import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from db import db

from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import BLACKLIST

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Flask JWT extended
# With below flask JWT can raise their own exceptions.
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = {"access", "refresh"}
app.secret_key = "2157$hiv"
# to keep your JWT secret key different from above.
# app.config["JWT_SECRET_KEY"]
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


# app.config["JWT_AUTH_URL_RULE"] = "/login"
# app.config["JWT_EXPIRATION_DELTA"] = timedelta(seconds=1800)
# app.config["JWT_AUTH_USERNAME_KEY"] = "email"

# jwt create a new end point called as "/auth"
# jwt = JWT(app, authenticate, identity)
jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:  # Instead of hard coding, should read from a config.ini / db.
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        "description": "The token has expired.",
        "error": "token_expired"
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "description": "Signature verification failed.",
        "error": "invalid_token: {error}".format(error)
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        "error": "authorization_required: {error}".format(error)
    }), 401


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(error):
    return jsonify({
        "description": "The token is not fresh.",
        "error": "fresh_token_required: {error}".format(error)
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token is not fresh.",
        "error": "fresh_token_required."
    }), 401


"""
@jwt.auth_responde_handler
def customized_response_handler(access_token, identity):
    return jsonify({
        "access_token": access_token.decode("utf-8"),
        "user_id": identity.id
    })

@jwt.error_handler
def customized_error_handler(error):
    return jsonify({
        "message": error.description,
        "code": error.status_code
    }), error.status_code
"""

api.add_resource(Store, "/store/<string:name>")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(StoreList, "/stores")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")

if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5001, debug=True)
