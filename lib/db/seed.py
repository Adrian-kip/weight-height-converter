from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.db.models import Base, User, Conversion
engine = create_engine('sqlite:///unit_converter.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

session.query(Conversion).delete()
session.query(User).delete()
session.commit()

user1 = User.create(session, name="Alice")
user2 = User.create(session, name="Bob")

Conversion.create(session, conversion_type="lbs_to_kg", input_value=150, result_value=68.04, user_id=user1.id)
Conversion.create(session, conversion_type="in_to_cm", input_value=70, result_value=177.8, user_id=user1.id)
Conversion.create(session, conversion_type="kg_to_lbs", input_value=90, result_value=198.42, user_id=user2.id)

print("Seeded database with test data.")
