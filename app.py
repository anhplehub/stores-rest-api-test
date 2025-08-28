import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager


from security import authenticate, identity
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.user import UserRegister

app = Flask(__name__)

app.config['JWT_HEADER_TYPE'] = 'Bearer'


app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'jose123'
jwt = JWTManager(app)
api = Api(app)

from flask_jwt_extended import create_access_token

@app.post('/auth')
def auth():
    from flask import request
    data = request.get_json()
    user = authenticate(data.get("username"), data.get("password"))
    if not user:
        return {"message": "Invalid credentials"}, 401
    return {"access_token": create_access_token(identity=str(user.id))}, 200

api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')

api.add_resource(UserRegister, '/register')



# Error handler replacement
@jwt.unauthorized_loader
def unauthorized_response(err):
    return jsonify({"message": "Could not authorize. Did you include an Authorization header?"}), 401



if __name__ == '__main__':
    from db import db

    db.init_app(app)

    if app.config['DEBUG']:
        #@app.before_first_request
        with app.app_context():
        #def create_tables():
            db.create_all()

    app.run(port=5000)
