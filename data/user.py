from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
import datetime


class UserCard(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    tg_id = sqlalchemy.Column(sqlalchemy.String(10), unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(100))
    capture = sqlalchemy.Column(sqlalchemy.String(255))
    picture = sqlalchemy.Column(sqlalchemy.String(255))
    old = sqlalchemy.Column(sqlalchemy.Integer)
    like = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    disabled = sqlalchemy.Column(sqlalchemy.Boolean)

    def __repr__(self):
        return f"<UserCard {self.name} ({self.tg_id})>"
