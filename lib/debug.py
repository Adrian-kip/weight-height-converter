from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.db.models import Base, User, Conversion

def debug_session():
    engine = create_engine('sqlite:///unit_converter.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("=== Current Users ===")
    users = User.get_all(session)
    for u in users:
        print(u)

    print("\n=== Adding a test user ===")
    new_user = User.create(session, name="DebugUser")
    print(f"Created: {new_user}")

    print("\n=== Current Users after adding ===")
    users = User.get_all(session)
    for u in users:
        print(u)

    print("\n=== Deleting the test user ===")
    new_user.delete(session)

    print("\n=== Current Users after deletion ===")
    users = User.get_all(session)
    for u in users:
        print(u)

    session.close()

if __name__ == "__main__":
    debug_session()
