import datetime
from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm


class U2U(SqlAlchemyBase):
    __tablename__ = 'u2u'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user1 = sqlalchemy.Column(sqlalchemy.Integer)
    like = sqlalchemy.Column(sqlalchemy.Integer)
    user2 = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<UserCard {self.name} ({self.tg_id})>"
