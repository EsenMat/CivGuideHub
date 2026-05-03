import datetime
import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


class Guides(SqlAlchemyBase):
    __tablename__ = 'guides'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    images = orm.relationship("Image", back_populates="guide")