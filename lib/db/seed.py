from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from lib.db.models import Base, User, Conversion

def initialize_database():
    engine = create_engine('sqlite:///unit_converter.db')
    

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        session.query(Conversion).delete()
        session.query(User).delete()
        
        user1 = User.create(session, name="Alice")
        user2 = User.create(session, name="Bob")
        
        Conversion.log_conversion(
            session,
            conv_type="lbs_to_kg",
            input_val=150,
            result_val=68.04,
            user_id=user1.id
        )
        
        Conversion.log_conversion(
            session,
            conv_type="in_to_cm",
            input_val=70,
            result_val=177.8,
            user_id=user1.id
        )
        
        Conversion.log_conversion(
            session,
            conv_type="kg_to_lbs",
            input_val=90,
            result_val=198.42,
            user_id=user2.id
        )
        
        session.commit()
        print("Successfully seeded database with test data.")
        
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    initialize_database()