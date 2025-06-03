# In your models.py (or wherever your models are defined)

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

# Association table for the many-to-many relationship
favorite_conversions = Table(
    'favorite_conversions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('conversion_id', Integer, ForeignKey('conversions.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)  
    
    conversions = relationship("Conversion", back_populates="user", cascade="all, delete-orphan")
    favorite_conversions = relationship(
        "Conversion",
        secondary=favorite_conversions,
        back_populates="favorited_by"
    )

    def __repr__(self):
        return f"User #{self.id}: {self.name}"

    @validates('name')
    def validate_name(self, key, name):
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty!")
        if len(name) > 50:
            raise ValueError("Name too long (max 50 chars)")
        return name

    @classmethod
    def find_by_id(cls, session, user_id):
        return cls.find(session, user_id)
    
    @classmethod
    def create(cls, session, name):
        try:
            new_user = cls(name=name)
            session.add(new_user)
            session.commit()
            return new_user
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")

    @classmethod
    def find(cls, session, user_id):
        return session.query(cls).get(user_id)

    @classmethod
    def get_all(cls, session): 
        return session.query(cls).order_by(cls.name).all()

    def remove(self, session):
        try:
            session.delete(self)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Failed to delete user: {str(e)}")
    
    def delete(self, session):
        session.delete(self)
        session.commit()

    def add_favorite(self, session, conversion):
        if conversion not in self.favorite_conversions:
            self.favorite_conversions.append(conversion)
            session.commit()
            return True
        return False

    def remove_favorite(self, session, conversion):
        if conversion in self.favorite_conversions:
            self.favorite_conversions.remove(conversion)
            session.commit()
            return True
        return False

class Conversion(Base):
    __tablename__ = 'conversions'

    id = Column(Integer, primary_key=True)
    conversion_type = Column(String(20), nullable=False) 
    input_value = Column(Float, nullable=False)
    result_value = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow) 
    input_unit = Column(String(10)) 
    output_unit = Column(String(10)) 

    user = relationship("User", back_populates="conversions")
    favorited_by = relationship(
        "User",
        secondary=favorite_conversions,
        back_populates="favorite_conversions"
    )

    def __repr__(self):
        return f"Conversion: {self.input_value}{self.input_unit}→{self.result_value}{self.output_unit} ({self.conversion_type})"

    @validates('conversion_type')
    def validate_conversion_type(self, key, conv_type):
        valid_types = ['lbs_to_kg', 'kg_to_lbs', 'in_to_cm', 'cm_to_in']
        if conv_type not in valid_types:
            raise ValueError(f"Invalid conversion type. Must be one of: {valid_types}")
        return conv_type

    @classmethod
    def log_conversion(cls, session, conv_type, input_val, result_val, user_id):
        try:
            units = {
                'lbs_to_kg': ('lbs', 'kg'),
                'kg_to_lbs': ('kg', 'lbs'),
                'in_to_cm': ('in', 'cm'),
                'cm_to_in': ('cm', 'in')
            }.get(conv_type, ('?', '?'))
            
            new_conv = cls(
                conversion_type=conv_type,
                input_value=input_val,
                result_value=result_val,
                user_id=user_id,
                input_unit=units[0],
                output_unit=units[1]
            )
            session.add(new_conv)
            session.commit()
            return new_conv
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Failed to log conversion: {str(e)}")
        
    @classmethod
    def create(cls, session, conversion_type, input_value, result_value, user_id):
        return cls.log_conversion(
            session=session,
            conv_type=conversion_type,
            input_val=input_value,
            result_val=result_value,
            user_id=user_id
        )

    @classmethod
    def get_user_history(cls, session, user_id):
        return session.query(cls).filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_recent(cls, session, limit=5):
        return session.query(cls).order_by(cls.created_at.desc()).limit(limit).all()

    def undo(self, session):
        try:
            session.delete(self)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Failed to undo conversion: {str(e)}")