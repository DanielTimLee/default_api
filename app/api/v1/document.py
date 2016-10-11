import arrow
from app import api_root, db, oauth_provider
from app.api.exceptions import BadRequestError
from app.api.marshals import document_field
from app.models.board import BoardModel
from app.models.document import DocumentModel
from app.api.exceptions import NotFoundError
from sqlalchemy.orm.exc import NoResultFound
from app.util.query.document import getDocumentQuery, getDocumentListQuery
from flask import request
from flask_restful import Resource, marshal_with, reqparse


@api_root.resource('/v1/document/<int:document_id>')
class Document(Resource):
    @oauth_provider.require_oauth('profile')
    @marshal_with(document_field)
    def get(self,document_id):

        document = DocumentModel.query.filter_by(id=document_id).first()

        document.read_count += 1
        db.session.commit()

        query = getDocumentQuery(document_id)
        result = query.first()

        output = dict(zip(result.keys(), result))

        return output

    @oauth_provider.require_oauth('profile')
    def put(self,document_id):

        document = DocumentModel.query.filter_by(id=document_id).first()

        query = getDocumentQuery(document_id)
        result = query.first()

        document.like_count += 1
        db.session.commit()

        return {
            'success': True,
            'messages': [
                '성공적으로 반영되었습니다.'
            ]
        }


@api_root.resource('/v1/document/<string:board_name>')
class DocumentList(Resource):
    @oauth_provider.require_oauth('profile')
    @marshal_with(document_field)
    def get(self, board_name):

        target_board = DocumentList.get_target_board(board_name)

        param_parser = reqparse.RequestParser()
        param_parser.add_argument('maxResult', type=int, default=10)
        args = param_parser.parse_args()

        # TODO : 쿼리 정리좀 해줘야 함.
        query = getDocumentListQuery().filter_by(board_id=target_board.id)
        result = query \
            .order_by(DocumentModel.id.desc()) \
            .limit(args.maxResult) \
            .all()

        output = list()
        for d in result:
            data = dict(zip(d.keys(), d))
            output.append(data)

        return output


    @oauth_provider.require_oauth('profile')
    def post(self,board_name):

        target_board = DocumentList.get_target_board(board_name)

        request_user = request.oauth.user
        request_body = request.get_json()

        new_document = DocumentModel(
            board_id=target_board.id,
            user_id=request_user.id,
            title=request_body['title'],
            content=request_body['content'],
            created_date=arrow.utcnow().datetime
        )

        db.session.add(new_document)
        db.session.commit()

        return {
            'success': True,
            'messages': [
                '정상적으로 작성되었습니다.'
            ]
        }


    @staticmethod
    def get_target_board(board_name):
        try:
            return BoardModel.query. \
                with_entities(BoardModel.id, BoardModel.is_anonymous). \
                filter_by(name=board_name). \
                one()

        except NoResultFound:
            raise NotFoundError
