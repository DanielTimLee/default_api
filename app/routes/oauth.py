import string

import arrow
import random
from app import app, oauth_provider, api_root, db
from app.api.exceptions import NotFoundError
from app.api.util import check_content_type
from app.forms.account import SignInForm
from app.models.bearer_token import BearerTokenModel
from app.models.client import ClientModel
from app.models.credential import CredentialModel
from app.models.grant_token import GrantTokenModel
from app.models.user import UserModel
from app.util.form import validate_on_submit
from flask import request, render_template
from flask_restful import Resource

permission_table = {
    'manager': [
        'profile', 'read_document', 'publish_document', 'read_comment', 'publish_comment', 'manage_users'
    ],
    'registered': [
        'profile', 'read_document', 'publish_document', 'read_comment', 'publish_comment'
    ],
    'unregistered': [
        'profile'
    ],
}


@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth_provider.authorize_handler
def authorize(*args, **kwargs):
    form = SignInForm(request.form)

    if validate_on_submit(form):
        req_username = form.username.data
        req_password = form.password.data

    else:
        return render_template('signin.html', form=form)

    user = UserModel.query. \
        filter_by(username=req_username). \
        first()

    if user is None:
        raise NotFoundError

    elif not (user.is_valid_password(req_password)):
        raise NotFoundError

    elif (user.type == 'withdrawal'):
        return {
                   'success': False,
                   'messages': [
                       '이미 탈퇴한 회원입니다..'
                   ]
               }, 404

    else:
        return True


@oauth_provider.clientgetter
def load_credential(client_id):
    return CredentialModel.query.filter_by(client_id=client_id).first()


@oauth_provider.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return BearerTokenModel.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return BearerTokenModel.query.filter_by(refresh_token=refresh_token).first()


@oauth_provider.tokensetter
def save_token(token, request, *args, **kwargs):
    credential = request.client
    user = request.user

    tokens = BearerTokenModel.query. \
        filter_by(app_id=credential.app_id, owner_id=user.id)

    for t in tokens:
        db.session.delete(t)

    # TODO: 토큰 발급 기간이 너무 길지만 나중에 수정
    expires = arrow.utcnow().replace(seconds=360000).datetime
    scopes = token['scope']

    issued_token = BearerTokenModel(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        scope=scopes,
        expires_date=expires,
        app_id=credential.app_id,
        owner_id=user.id
    )

    db.session.add(issued_token)
    db.session.commit()
    return issued_token


@oauth_provider.grantsetter
def save_grant(client_id, code, requests, *args, **kwargs):
    request_body = check_content_type()

    resource_owner = UserModel.query. \
        with_entities(UserModel.id, UserModel.type). \
        filter_by(username=request_body['username']). \
        one()

    app_credential = CredentialModel.query.filter_by(client_id=client_id).one()

    expires = arrow.utcnow().replace(seconds=3600).datetime

    grant = GrantTokenModel(
        app_id=app_credential.application.id,
        code=code['code'],
        redirect_uri=requests.redirect_uri,
        scope=' '.join(permission_table[resource_owner.type]),
        owner_id=resource_owner.id,
        expires_date=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth_provider.grantgetter
def load_grant(client_id, code):
    app_credential = CredentialModel.query. \
        with_entities(CredentialModel.app_id). \
        filter_by(client_id=client_id). \
        one()

    return GrantTokenModel.query.filter_by(app_id=app_credential.app_id, code=code).one()


@app.route('/oauth/token', methods=['POST'])
@oauth_provider.token_handler
def access_token():
    return None


@api_root.resource('/oauth/application')
class Applications(Resource):
    def post(self):
        data = request.get_json()
        new_app = ClientModel(data['name'])

        db.session.add(new_app)
        db.session.commit()

        return {
                   'name': data['name']
               }, 201


@api_root.resource('/oauth/credential')
class Credentials(Resource):
    def post(self):
        data = request.get_json()
        target_app = ClientModel. \
            query. \
            with_entities(ClientModel.id, ClientModel.name). \
            filter_by(name=data['application']). \
            first()

        rand_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

        client_id = "{0}-{1}".format(target_app.name, rand_str)

        new_credential = CredentialModel(
            application_id=target_app.id,
            client_id=client_id,
            platform=data['platform'],
            white_list=data['whitelist'],
            callback=data['callback'],
            scopes=data['scopes'])

        db.session.add(new_credential)
        db.session.commit()

        return {
                   'client_id': client_id
               }, 201
