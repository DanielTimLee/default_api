import datetime
import time

import hashlib
from app import db
from sqlalchemy.dialects.mysql import BIGINT, TEXT, TIMESTAMP
from sqlalchemy.sql.expression import text


class CredentialModel(db.Model):
    __tablename__ = 'credentials'
    __table_args__ = {
        'mysql_charset': 'utf8',
        'extend_existing': True
    }

    platform_enum = ('web', 'server', 'ios', 'android')
    client_type_enum = ('public', 'confidential')

    id = db.Column(
        BIGINT(20, unsigned=True),
        primary_key=True,
        autoincrement=True,
        index=True
    )
    app_id = db.Column(
        BIGINT(20, unsigned=True),
        db.ForeignKey('clients.id', ondelete='CASCADE'),
        nullable=False
    )
    application = db.relationship('ClientModel', backref='credential', lazy='joined')
    client_id = db.Column(
        db.String(255),
        nullable=False
    )
    client_secret = db.Column(
        db.String(255),
        nullable=False
    )
    client_type = db.Column(
        db.Enum(*client_type_enum),
        nullable=False,
        server_default='public'
    )
    platform = db.Column(
        db.Enum(*platform_enum),
        nullable=False
    )
    white_list = db.Column(
        TEXT,
        nullable=False
    )
    callback = db.Column(
        TEXT,
        nullable=False
    )
    scopes = db.Column(
        TEXT,
        nullable=False
    )
    created_date = db.Column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=text('CURRENT_TIMESTAMP')
    )
    updated_date = db.Column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    def __init__(self, application_id, client_id, platform, white_list, callback, scopes):
        self.app_id = application_id
        self.client_id = client_id

        source_str = "{0}-{1}-{2}".format(client_id, time.time(), 'app')
        self.client_secret = hashlib.sha256(source_str.encode('utf-8')).hexdigest()
        self.platform = platform
        self.set_white_list(white_list)
        self.set_callback(callback)
        self.set_scopes(scopes)
        self.created_date = datetime.datetime.utcnow()
        self.updated_date = datetime.datetime.utcnow()

    def set_white_list(self, white_list):
        self.white_list = ','.join(white_list)

    def set_callback(self, callbacks):
        self.callback = ','.join(callbacks)

    def set_scopes(self, scopes):
        self.scopes = ','.join(scopes)

    @property
    def redirect_uris(self):
        if self.callback:
            return self.callback.split(',')
        return []

    @property
    def default_redirect_uri(self):
        return self.application.default_redirect_uri

    @property
    def default_scopes(self):
        if self.scopes:
            return self.scopes.split(',')
        return ['profile']
