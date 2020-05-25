from flask_restful import Resource

from models.store import StoreModel


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.to_json(), 200  # default status code, may be omitted
        return {'Message': 'Store not found'}, 404  # not found

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'Message:': f'A store with id {name} already exists'}, 400  # bad request

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {'Message:': 'An error occured during insertion'}, 500  # Internal server error

        return store.to_json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db() # 'DELETE FROM items WHERE name=?'

        return {'message': 'Store deleted'}




class StoreList(Resource):
    def get(self):
        # return {'items': list(map(lambda x: x.to_json(), ItemModel.query.all()))}
        return {'stores': [store.to_json() for store in StoreModel.query.all()]}
