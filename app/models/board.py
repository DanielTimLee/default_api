import datetime

from app import app, db
from sqlalchemy.dialects.mysql import INTEGER, TIMESTAMP
from sqlalchemy.sql.expression import text


class BoardModel(db.Model):
    __tablename__ = 'boards'
    __table_args__ = {
        'mysql_charset': 'utf8',
        'extend_existing': True
    }

    id = db.Column(
        INTEGER(20, unsigned=True),
        primary_key=True,
        index=True
    )
    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )
    title = db.Column(
        db.String(100),
        nullable=False
    )
    created_date = db.Column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=text('CURRENT_TIMESTAMP')
    )

    documents = db.relationship(
        'DocumentModel',
        backref='board',
        lazy='dynamic'
    )
