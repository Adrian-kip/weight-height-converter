from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, validates

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    conversions = relationship("Conversion", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"

    @validates('name')
    def validate_name(self, key, value):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        return value

    @classmethod
    def create(cls, session, name):
        user = cls(name=name)
        session.add(user)
        session.commit()
        return user

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def find_by_id(cls, session, user_id):
        return session.query(cls).filter_by(id=user_id).first()

    def delete(self, session):
        session.delete(self)
        session.commit()


class Conversion(Base):
    __tablename__ = 'conversions'

    id = Column(Integer, primary_key=True)
    conversion_type = Column(String, nullable=False)
    input_value = Column(Float, nullable=False)
    result_value = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="conversions")

    def __repr__(self):
        return f"<Conversion(type={self.conversion_type}, {self.input_value} -> {self.result_value})>"

    @classmethod
    def create(cls, session, conversion_type, input_value, result_value, user_id):
        conversion = cls(
            conversion_type=conversion_type,
            input_value=input_value,
            result_value=result_value,
            user_id=user_id
        )
        session.add(conversion)
        session.commit()
        return conversion

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def find_by_id(cls, session, conv_id):
        return session.query(cls).filter_by(id=conv_id).first()

    def delete(self, session):
        session.delete(self)
        session.commit()
