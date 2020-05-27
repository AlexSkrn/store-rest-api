from flask_restful import reqparse
from flask_restful import Resource

from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    fresh_jwt_required
    )
from flask_jwt_extended import get_jwt_identity

from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left blank'
                        )
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help='Every item needs a store id'
                        )

    @jwt_required  # not jwt_required() now compared to flask-jwt
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.to_json(), 200
        return {'Message': 'Item not found'}, 404  # not found

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'Message:': f'An item with name {name} already exists'}, 400  # bad request

        data = type(self).parser.parse_args()
        item = ItemModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {'Message:': 'An error occured during insertion'}, 500  # Internal server error

        return item.to_json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'Message': 'Admin privilege required'}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()  # 'DELETE FROM items WHERE name=?'

        return {'message': 'Item deleted'}

    def put(self, name):
        data = type(self).parser.parse_args()

        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()

        return item.to_json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        print(user_id)
        items = [item.to_json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {
                'items': [item['name'] for item in items],
                'Message': 'More data available if you log in'
                }, 200
