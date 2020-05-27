from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
    )

from models.user import UserModel

from blacklist import BLACKLIST


_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
                    'username',
                    type=str,
                    required=True,
                    help='This field cannot be left blank'
                    )
_user_parser.add_argument(
                    'password',
                    type=str,
                    required=True,
                    help='This field cannot be left blank'
                    )


class UserRegister(Resource):
    """Provide a class to create users."""

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'Message': 'User with such username already exists'}, 400  # Bad Request

        user = UserModel(**data)
        user.save_to_db()  # 'INSERT INTO users VALUES (NULL, ?, ?)'

        return {'Message': 'User created successfully'}, 201  # Created


class User(Resource):
    """Provide a class for testing the interface."""

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.to_json()
        return {'Message': f'No user with id {user_id}'}, 404

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {'Message': 'User deleted'}, 200
        return {'Message': 'User not found'}, 404


class UserLogin(Resource):
    @classmethod
    def post(cls):
        """Create access token for authorized user."""
        # get data from parser
        data = _user_parser.parse_args()
        # find user in database
        user = UserModel.find_by_username(data['username'])
        # check password
        # this is what authenticate() used to do
        if user and safe_str_cmp(user.password, data['password']):
            # identity= is what identity() used to do
            access_token = create_access_token(identity=user.id,
                                               fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {'Message': 'Invalid credentials'}, 401  # Unauthorized


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # unique jwt id
        BLACKLIST.add(jti)
        return {'Message': 'Successfully logged out.'}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user,
                                        fresh=False
                                        )
        return {'access_token': new_token}, 200
