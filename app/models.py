from app import db_session,Base
from sqlalchemy import Column, Integer, String, Boolean, BLOB

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    steam_id = Column(String(40))
    nickname = Column(String(80))
    email = Column(String(80))


    @staticmethod
    def get_or_create(steam_id):
        rv = User.query.filter_by(steam_id=steam_id).first()
        if rv is None:
            rv = User()
            rv.steam_id = steam_id
            db_session.add(rv)
        return rv

    def __repr__(self):
        """docstring for __repr__"""
        return self.nickname