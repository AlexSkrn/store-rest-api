from flask_restful import reqparse
from flask_restful import Resource

from flask_jwt import jwt_required

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

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.to_json(), 200
        return {'Message': 'Item not found'}, 404  # not found

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'Message:': f'An item with name {name} already exists'}, 400  # bad request

        data = type(self).parser.parse_args()
        item = ItemModel(name, data['price'], data['store_id'])
        try:
            item.save_to_db()
        except:
            return {'Message:': 'An error occured during insertion'}, 500  # Internal server error

        return item.to_json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db() # 'DELETE FROM items WHERE name=?'

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
    def get(self):
        # return {'items': list(map(lambda x: x.to_json(), ItemModel.query.all()))}
        return {'items': [item.to_json() for item in ItemModel.query.all()]}
