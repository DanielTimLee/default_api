import datetime

from app import db
from sqlalchemy.dialects.mysql import BIGINT, TEXT, TIMESTAMP, DATETIME
from sqlalchemy.sql.expression import text


class GrantTokenModel(db.Model):
    __tablename__ = 'grant_tokens'
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
    owner_id = db.Column(
        BIGINT(20, unsigned=True),
        db.ForeignKey('users.id'),
        nullable=False
    )
    user = db.relationship('UserModel',
                           backref='grant_token',
                           lazy='joined')
    code = db.Column(
        db.String(255),
        nullable=False
    )
    expires_date = db.Column(
        DATETIME,
        nullable=False
    )
    redirect_uri = db.Column(
        db.String(255),
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

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []
