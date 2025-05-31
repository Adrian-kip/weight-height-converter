import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.db.models import Base, User, Conversion
from lib.helpers import get_conversion_result

engine = create_engine('sqlite:///unit_converter.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_valid_choice(prompt, options):
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print(f"Invalid choice. Please enter one of {options}.")


def get_valid_float(prompt):
    while True:
        val = input(prompt).strip()
        try:
            return float(val)
        except ValueError:
            print("Invalid number. Please enter a valid numeric value.")


def main_menu():
    session = Session()
    while True:
        print("\n=== Unit Converter CLI ===")
        print("1. Manage Users")
        print("2. Perform Conversion")
        print("3. View User Conversion History")
        print("4. Exit")

        choice = get_valid_choice("Select an option: ", ['1', '2', '3', '4'])

        if choice == '1':
            manage_users(session)
        elif choice == '2':
            perform_conversion(session)
        elif choice == '3':
            view_conversion_history(session)
        elif choice == '4':
            print("Goodbye!")
            session.close()
            sys.exit()


def manage_users(session):
    while True:
        print("\n--- Manage Users ---")
        print("1. Create User")
        print("2. Delete User")
        print("3. List All Users")
        print("4. Find User by ID")
        print("5. Return to Main Menu")

        choice = get_valid_choice("Select an option: ", ['1', '2', '3', '4', '5'])

        if choice == '1':
            name = input("Enter new user name: ").strip()
            if name:
                try:
                    user = User.create(session, name=name)
                    print(f"User created: {user}")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Name cannot be empty.")
        elif choice == '2':
            user_id = input("Enter user ID to delete: ").strip()
            if user_id.isdigit():
                user = User.find_by_id(session, int(user_id))
                if user:
                    confirm = input(f"Are you sure you want to delete user '{user.name}'? (y/n): ").lower()
                    if confirm == 'y':
                        user.delete(session)
                        print("User deleted.")
                else:
                    print("User not found.")
            else:
                print("Invalid user ID.")
        elif choice == '3':
            users = User.get_all(session)
            if users:
                print("\nUsers:")
                for user in users:
                    print(f"ID: {user.id}, Name: {user.name}")
            else:
                print("No users found.")
        elif choice == '4':
            user_id = input("Enter user ID to find: ").strip()
            if user_id.isdigit():
                user = User.find_by_id(session, int(user_id))
                if user:
                    print(f"Found user: ID={user.id}, Name={user.name}")
                else:
                    print("User not found.")
            else:
                print("Invalid user ID.")
        elif choice == '5':
            break


def perform_conversion(session):
    users = User.get_all(session)
    if not users:
        print("No users found. Please create a user first.")
        return

    print("\nSelect user for this conversion:")
    for user in users:
        print(f"{user.id}. {user.name}")

    user_id = input("Enter user ID: ").strip()
    if not user_id.isdigit():
        print("Invalid user ID.")
        return

    user = User.find_by_id(session, int(user_id))
    if not user:
        print("User not found.")
        return

    print("\nSelect conversion type:")
    print("1. lbs to kg")
    print("2. kg to lbs")
    print("3. inches to cm")
    print("4. cm to inches")

    conversion_map = {
        '1': ("lbs_to_kg", "lbs", "kg"),
        '2': ("kg_to_lbs", "kg", "lbs"),
        '3': ("in_to_cm", "inches", "cm"),
        '4': ("cm_to_in", "cm", "inches")
    }

    conv_choice = get_valid_choice("Select an option: ", conversion_map.keys())
    conv_type, unit_in, unit_out = conversion_map[conv_choice]

    input_value = get_valid_float(f"Enter the value to convert ({unit_in}): ")

    try:
        result = get_conversion_result(conv_type, input_value)
        conversion_record = Conversion.create(session,
                                             conversion_type=conv_type,
                                             input_value=input_value,
                                             result_value=result,
                                             user_id=user.id)
        print(f"Conversion result: {input_value:.2f} {unit_in} -> {result:.2f} {unit_out}")
        print(f"Conversion saved for user '{user.name}'.")
    except ValueError as e:
        print(f"Conversion error: {e}")


def view_conversion_history(session):
    users = User.get_all(session)
    if not users:
        print("No users found.")
        return

    print("\nSelect user to view conversion history:")
    for user in users:
        print(f"{user.id}. {user.name}")

    user_id = input("Enter user ID: ").strip()
    if not user_id.isdigit():
        print("Invalid user ID.")
        return

    user = User.find_by_id(session, int(user_id))
    if not user:
        print("User not found.")
        return

    if not user.conversions:
        print(f"No conversions found for user '{user.name}'.")
        return

    print(f"\nConversion history for user '{user.name}':")
    for conv in user.conversions:
        unit_in, unit_out = "", ""
        if conv.conversion_type == "lbs_to_kg":
            unit_in, unit_out = "lbs", "kg"
        elif conv.conversion_type == "kg_to_lbs":
            unit_in, unit_out = "kg", "lbs"
        elif conv.conversion_type == "in_to_cm":
            unit_in, unit_out = "inches", "cm"
        elif conv.conversion_type == "cm_to_in":
            unit_in, unit_out = "cm", "inches"

        print(f"ID: {conv.id}, {conv.input_value:.2f} {unit_in} -> {conv.result_value:.2f} {unit_out}")


if __name__ == '__main__':
    main_menu()
