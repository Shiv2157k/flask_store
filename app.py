import os

from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList

from db import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "2157$hiv"
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()

#app.config["JWT_AUTH_URL_RULE"] = "/login"
#app.config["JWT_EXPIRATION_DELTA"] = timedelta(seconds=1800)
#app.config["JWT_AUTH_USERNAME_KEY"] = "email"

# jwt create a new end point called as "/auth"
jwt = JWT(app, authenticate, identity)

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

if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5001, debug=True)
