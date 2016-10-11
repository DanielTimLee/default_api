import datetime

from app import db
from sqlalchemy.dialects.mysql import BIGINT, TEXT, TIMESTAMP, DATETIME
from sqlalchemy.sql.expression import text


class BearerTokenModel(db.Model):
    __tablename__ = 'bearer_tokens'
    __table_args__ = {
        'mysql_charset': 'utf8',
        'extend_existing': True
    }

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
    application = db.relationship('ClientModel', lazy='joined')
    owner_id = db.Column(
        BIGINT(20, unsigned=True),
        db.ForeignKey('users.id'),
        nullable=False
    )
    user = db.relationship('UserModel',
                           backref='bearer_token',
                           lazy='joined')
    token_type = db.Column(
        db.String(80),
        nullable=False
    )
    access_token = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    refresh_token = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    expires_date = db.Column(
        DATETIME,
        nullable=False
    )
    scope = db.Column(
        TEXT,
        nullable=False
    )
    created_date = db.Column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=text('CURRENT_TIMESTAMP')
    )

    @property
    def client_id(self):
        credential = self.application.credential
        if credential is None:
            return None
        return credential[0].client_id

    @property
    def expires(self):
        return self.expires_date

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []
