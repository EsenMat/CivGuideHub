from flask_restful import reqparse, abort, Api, Resource, inputs
from flask import Flask, jsonify
from data import db_session
from data.guides import Guides


parser = reqparse.RequestParser()
parser.add_argument('type', required=True)
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('created_date', required=True, type=inputs.datetime_from_iso8601)
parser.add_argument('user_id', required=True, type=int)



def abort_if_guides_not_found(guides_id):
    session = db_session.create_session()
    guides = session.query(Guides).get(guides_id)
    if not guides:
        abort(404, message=f"News {guides_id} not found")


class GuidesResource(Resource):
    def get(self, guides_id):
        abort_if_guides_not_found(guides_id)
        session = db_session.create_session()
        guides = session.get(Guides, guides_id)
        return jsonify({'guides': guides.to_dict(
            only=('type', 'title', 'content', 'created_date', 'user_id'))})

    def delete(self, guides_id):
        abort_if_guides_not_found(guides_id)
        session = db_session.create_session()
        guides = session.get(Guides, guides_id)
        session.delete(guides)
        session.commit()
        return jsonify({'success': 'OK'})


class GuidesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        guides = session.query(Guides).all()
        return jsonify({'guides': [item.to_dict(
            only=('type', 'title', 'content', 'created_date', 'user.name')) for item in guides]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        guides = Guides(
            type=args['type'],
            title=args['title'],
            content=args['content'],
            created_date=args['created_date'],
            user_id=args['user_id'],
        )
        session.add(guides)
        session.commit()
        return jsonify({'id': guides.id})