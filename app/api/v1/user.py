import arrow
from app import bcrypt, api_root, db, oauth_provider
from app.api.exceptions import BadRequestError
from app.api.exceptions import ConflictError, UnauthorizedError
from app.api.marshals import user_field
from app.models.user import UserModel
from flask import request, jsonify
from flask_restful import Resource, marshal_with, reqparse
from sqlalchemy.exc import IntegrityError


@api_root.resource('/v1/account')
class Account(Resource):
    def post(self):
        request_body = request.get_json()
        new_user = UserModel(
            username=request_body['username'],
            password=bcrypt.generate_password_hash(request_body['password']),
            email=request_body['email'],
            created_date=arrow.utcnow().datetime
        )

        # TODO: 이메일 발송 처리
        # SendAuthMail(email=request_body['email'], subject=,contents=)
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            raise ConflictError
        return {
            'success': True,
            'messages': [
                '인증 메일이 발송되었습니다! 이메일을 확인해 주세요!'
            ]
        }

    @oauth_provider.require_oauth('profile')
    @marshal_with(user_field)
    def get(self):
        request_user = request.oauth.user
        query = UserModel.query.filter_by(id=request_user.id)

        item = query.first()

        return item

    @oauth_provider.require_oauth('profile')
    @marshal_with(user_field)
    def put(self):
        request_user = request.oauth.user
        request_body = request.get_json()

        # TODO : 로직이 좀 이상함. 프로필 수정에는 verify를 하고 넘어오고 비밀번호 변경시에는 같이 비교함

        if request_body['new_password']:
            user = UserModel.query.filter_by(id=request_user.id).first()

            if not user.is_valid_password(request_body['password']):
                return {
                    'success': False,
                    'messages': [
                        '잘못된 비밀번호입니다.'
                    ]
                }

            else:
                user.password=bcrypt.generate_password_hash(request_body['new_password'])

        elif not request_body['nickname']:
            # TODO:사용자가 닉네임을 수정하지 않고 그냥 보내는 경우에는?
            # TODO:닉네임이 중복될 경우에는?
            is_nickname = UserModel.query.filter_by(nickname=request_body['nickname']).first()

            query = UserModel.query.filter_by(id=request_user.id)
            user = query.first()

            user.name = request_body['name']
            user.nickname = request_body['nickname']
            user.gender = request_body['gender']

        db.session.commit()

        return user

    @oauth_provider.require_oauth('profile')
    def delete(self):
        request_user = request.oauth.user
        request_body = request.get_json()

        query = UserModel.query.filter_by(id=request_user.id)
        user = query.first()

        if (user.type == 'withdrawal'):
            raise ConflictError

        if (user.username != request_body['username']):
            raise UnauthorizedError

        if not (user.is_valid_password(request_body['password'])):
            raise UnauthorizedError

        user.type = 'withdrawal'

        db.session.commit()

        return {
            'success': True,
            'messages': [
                '정상적으로 탈퇴처리 되었습니다.'
            ]
        }



@api_root.resource('/v1/account/verify')
class UserVerify(Resource):
    def get(self):
        param_parser = reqparse.RequestParser()
        param_parser.add_argument('username', type=str, default=None)
        args = param_parser.parse_args()

        if args.username is None:
            raise BadRequestError

        user = UserModel.query.filter_by(username=args.username).first()

        if user is None:
            data = {"is_user": "false", "is_first": "true"}
            return jsonify(data)

        if user.nickname is None:
            data = {"is_user": "true", "is_first": "true"}
            return jsonify(data)

        data = {"is_user": "true", "is_first": "false"}
        return jsonify(data)

    @oauth_provider.require_oauth('profile')
    def post(self):
        request_user = request.oauth.user

        request_body = request.get_json()

        if not request_user.is_valid_password(request_body['password']):
            return {
                'success': False,
                'messages': [
                    '잘못된 비밀번호입니다.'
                ]
            }

        return {
            'success': True,
            'messages': [
                '비밀번호가 정상적으로 확인되었습니다.'
            ]
        }
