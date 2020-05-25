import sqlite3

from flask_restful import Resource, reqparse

from models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help='This field cannot be left blank'
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help='This field cannot be left blank'
                        )

    def post(self):
        data = type(self).parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'Message': 'User with such username already exists'}, 400  # Bad Request

        user = UserModel(**data)
        user.save_to_db()  # 'INSERT INTO users VALUES (NULL, ?, ?)'

        return {'Message': 'User created successfully'}, 201  # Created
