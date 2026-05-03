import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


class Image(SqlAlchemyBase):
    __tablename__ = 'images'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    guide_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("guides.id"))
    guide = orm.relationship('Guides', back_populates='images')