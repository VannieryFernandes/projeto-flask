from flask import Flask,jsonify,request,Response
import json
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
json_encode = json.JSONEncoder().encode
app = Flask(__name__)
api = Api(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'projeto.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'email')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def abort_if_user_doesnt_exist(user_id):
    user = User.query.get(user_id)
    print(user)
    if user == None:
        abort(404, message="Usuario {} não existe".format(user_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


class CreateUser(Resource):
     def post(self):
        username = request.json['username']
        email = request.json['email']
        new_user = User(username, email)
        db.session.add(new_user)
        db.session.commit()
        
        return  Response(json_encode({'result':user_schema.dump(new_user)}),mimetype="application/json")


class UserController(Resource):

    def get(self, user_id):
        user = User.query.get(user_id)
        abort_if_user_doesnt_exist(user_id)
        result = user_schema.dump(user)

        return Response(json_encode(result),mimetype="application/json")

    def delete(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        user = (user_schema.dump(user))

        return Response(json_encode(user),mimetype="application/json")

    def put(self, user_id):
        username = request.json['username']
        email = request.json['email']
        abort_if_user_doesnt_exist(user_id)
        user = User.query.get(user_id)
        user.email = email
        user.username = username
        db.session.commit()
        return Response(json_encode({'result': user_schema.dump(user)}),mimetype="application/json")


class UserList(Resource):
    def get(self):
        all_users = User.query.all()
        result = users_schema.dump(all_users)
        return Response(json_encode({'result':result}),mimetype="application/json")


api.add_resource(UserList, '/usuarios')
api.add_resource(UserController, '/usuario/<user_id>')
api.add_resource(CreateUser, '/usuario/new')


if __name__ == '__main__':
    app.run(debug=True)