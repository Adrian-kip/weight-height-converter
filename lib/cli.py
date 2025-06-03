"""
Unit Converter CLI Application
Author: [Adrian Kiptoo]
Date: [31st June 2025]

A simple command-line tool for unit conversions with user management.
Uses SQLAlchemy for database operations.
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.db.models import Base, User, Conversion
from lib.helpers import get_conversion_result

engine = create_engine('sqlite:///unit_converter.db')
Base.metadata.create_all(engine) 
Session = sessionmaker(bind=engine) 

def get_valid_choice(prompt, options):
    """Keeps asking until we get a valid choice"""
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print(f"Oops! Please choose one of these: {options}")

def get_valid_float(prompt):
    """Makes sure we get a proper number"""
    while True:
        val = input(prompt).strip()
        try:
            return float(val)
        except ValueError:
            print("That's not a valid number. Try again please.")

def main_menu():
    """Handles the main program flow"""
    session = Session()
    try:
        while True:
            print("\n=== Unit Converter ===")
            print("What would you like to do?")
            print("1. Manage Users")
            print("2. Do a Conversion")
            print("3. Check Conversion History")
            print("4. Quit")

            choice = get_valid_choice("Your choice: ", ['1', '2', '3', '4'])

            if choice == '1':
                manage_users(session)
            elif choice == '2':
                perform_conversion(session)
            elif choice == '3':
                view_conversion_history(session)
            elif choice == '4':
                print("Thanks for using the converter! Goodbye!")
                session.close()
                sys.exit()
    except Exception as e:
        print(f"Hehehe! Something went wrong: {e}")
        session.close()

def manage_users(session):
    """Handles all the user-related operations"""
    while True:
        print("\n--- User Manager ---")
        print("Options:")
        print("1. Add New User")
        print("2. Remove User")
        print("3. Show All Users")
        print("4. Find Specific User")
        print("5. Back to Main Menu")

        choice = get_valid_choice("Pick an option (1-5): ", ['1', '2', '3', '4', '5'])

        if choice == '1':
            name = input("What's the new user's name? ").strip()
            if not name:
                print("Wee bana, tunahitaji jina!")
                continue
                
            try:
                user = User.create(session, name=name)
                print(f"Success! Created user: {user.name} (ID: {user.id})")
            except Exception as e:
                print(f"Uh oh, couldn't create user: {e}")
        
        elif choice == '2':
            user_id = input("Which user ID to remove? ").strip()
            if not user_id.isdigit():
                print("That doesn't look like a valid ID")
                continue
                
            user = User.find_by_id(session, int(user_id))
            if not user:
                print("Can't find that user, sorry!")
                continue
                
            confirm = input(f"Really delete {user.name}? (y/n): ").lower()
            if confirm == 'y':
                user.delete(session)
                print("User deleted.")
            else:
                print("Phew, that was close!")
        
        elif choice == '3':
            users = User.get_all(session)
            if not users:
                print("No users yet - the system feels lonely!")
                continue
                
            print("\nCurrent Users:")
            for user in users:
                print(f"  {user.id}: {user.name}")
        
        elif choice == '4':
            user_id = input("Enter user ID to find: ").strip()
            if not user_id.isdigit():
                print("IDs are numbers, try again")
                continue
                
            user = User.find_by_id(session, int(user_id))
            if user:
                print(f"Found: {user.name} (ID: {user.id})")
            else:
                print("No user with that ID exists")
        
        elif choice == '5':
            break

def perform_conversion(session):
    """Handles the unit conversion process"""
    users = User.get_all(session)
    if not users:
        print("No users exist yet - create one first!")
        return

    print("\nWho's doing this conversion?")
    for user in users:
        print(f"{user.id}. {user.name}")

    user_id = input("Enter user ID: ").strip()
    if not user_id.isdigit():
        print("That's not a valid ID number")
        return

    user = User.find_by_id(session, int(user_id))
    if not user:
        print("Couldn't find that user")
        return

    print("\nWhat kind of conversion?")
    print("1. Pounds to Kilograms")
    print("2. Kilograms to Pounds")
    print("3. Inches to Centimeters")
    print("4. Centimeters to Inches")

    conversion_map = {
        '1': ("lbs_to_kg", "lbs", "kg"),
        '2': ("kg_to_lbs", "kg", "lbs"),
        '3': ("in_to_cm", "inches", "cm"),
        '4': ("cm_to_in", "cm", "inches")
    }

    conv_choice = get_valid_choice("Your choice (1-4): ", conversion_map.keys())
    conv_type, unit_in, unit_out = conversion_map[conv_choice]

    input_value = get_valid_float(f"Enter value in {unit_in}: ")

    try:
        result = get_conversion_result(conv_type, input_value)
        Conversion.create(
            session,
            conversion_type=conv_type,
            input_value=input_value,
            result_value=result,
            user_id=user.id
        )
        print(f"\nResult: {input_value:.2f} {unit_in} = {result:.2f} {unit_out}")
        print(f"(Saved to {user.name}'s history)")
    except ValueError as e:
        print(f"Conversion failed: {e}")

def view_conversion_history(session):
    """Shows previous conversions for a user"""
    users = User.get_all(session)
    if not users:
        print("No users in the system yet!")
        return

    print("\nWhose history should we check?")
    for user in users:
        print(f"{user.id}. {user.name}")

    user_id = input("Enter user ID: ").strip()
    if not user_id.isdigit():
        print("IDs are numbers, remember?")
        return

    user = User.find_by_id(session, int(user_id))
    if not user:
        print("No user with that ID")
        return

    if not user.conversions:
        print(f"\n{user.name} hasn't done any conversions yet!")
        return

    print(f"\n{user.name}'s Conversion History:")
    for conv in user.conversions:
        if conv.conversion_type == "lbs_to_kg":
            units = ("lbs", "kg")
        elif conv.conversion_type == "kg_to_lbs":
            units = ("kg", "lbs")
        elif conv.conversion_type == "in_to_cm":
            units = ("inches", "cm")
        elif conv.conversion_type == "cm_to_in":
            units = ("cm", "inches")
        else:
            units = ("?", "?")
            
        print(f"  {conv.input_value:.2f} {units[0]} → {conv.result_value:.2f} {units[1]}")

if __name__ == '__main__':
    print("Welcome to the Unit Converter!")
    main_menu()