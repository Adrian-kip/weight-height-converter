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
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print(f"Oops! Please choose one of these: {options}")

def get_valid_float(prompt):
    while True:
        val = input(prompt).strip()
        try:
            return float(val)
        except ValueError:
            print("That's not a valid number. Try again please.")

def get_valid_int(prompt):
    while True:
        val = input(prompt).strip()
        if val.isdigit():
            return int(val)
        print("Please enter a valid integer.")

def main_menu():
    session = Session()
    try:
        while True:
            print("\n=== Unit Converter ===")
            print("What would you like to do?")
            print("1. Manage Users")
            print("2. Do a Conversion")
            print("3. Check Conversion History")
            print("4. Manage Favorites")
            print("5. Quit")

            choice = get_valid_choice("Your choice: ", ['1', '2', '3', '4', '5'])

            if choice == '1':
                manage_users(session)
            elif choice == '2':
                perform_conversion(session)
            elif choice == '3':
                view_conversion_history(session)
            elif choice == '4':
                manage_favorites_menu(session)
            elif choice == '5':
                print("Thanks for using the converter! Goodbye!")
                session.close()
                sys.exit()
    except Exception as e:
        print(f"Something went wrong: {e}")
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
                print("Name cannot be empty!")
                continue
                
            try:
                user = User.create(session, name=name)
                print(f"Success! Created user: {user.name} (ID: {user.id})")
            except Exception as e:
                print(f"Couldn't create user: {e}")
        
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
                print("Operation cancelled.")
        
        elif choice == '3':
            users = User.get_all(session)
            if not users:
                print("No users yet!")
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
    users = User.get_all(session)
    if not users:
        print("No users exist yet - create one first!")
        return

    print("\nWho's doing this conversion?")
    for user in users:
        print(f"{user.id}. {user.name}")

    user_id = get_valid_int("Enter user ID: ")
    user = User.find_by_id(session, user_id)
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
        conversion = Conversion.create(
            session,
            conversion_type=conv_type,
            input_value=input_value,
            result_value=result,
            user_id=user.id
        )
        print(f"\nResult: {input_value:.2f} {unit_in} = {result:.2f} {unit_out}")
        print(f"(Saved to {user.name}'s history)")
        
        # Ask if user wants to favorite this conversion
        favorite = input("Would you like to favorite this conversion? (y/n): ").lower()
        if favorite == 'y':
            user.add_favorite(session, conversion)
            print("Added to favorites!")
            
    except ValueError as e:
        print(f"Conversion failed: {e}")

def view_conversion_history(session):
    users = User.get_all(session)
    if not users:
        print("No users in the system yet!")
        return

    print("\nWhose history should we check?")
    for user in users:
        print(f"{user.id}. {user.name}")

    user_id = get_valid_int("Enter user ID: ")
    user = User.find_by_id(session, user_id)
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
            
        favorite_indicator = "★" if conv in user.favorite_conversions else ""
        print(f"  {conv.id}: {conv.input_value:.2f} {units[0]} → {conv.result_value:.2f} {units[1]} {favorite_indicator}")

def manage_favorites_menu(session):
    users = User.get_all(session)
    if not users:
        print("No users in the system yet!")
        return

    print("\nSelect a user to manage favorites:")
    for user in users:
        print(f"{user.id}. {user.name}")

    user_id = get_valid_int("Enter user ID: ")
    user = User.find_by_id(session, user_id)
    if not user:
        print("No user with that ID")
        return

    manage_favorites(session, user)

def manage_favorites(session, user):
    while True:
        print(f"\n--- {user.name}'s Favorite Conversions ---")
        print("1. View Favorites")
        print("2. Add Favorite")
        print("3. Remove Favorite")
        print("4. Back to Main Menu")
        
        choice = get_valid_choice("Pick an option (1-4): ", ['1', '2', '3', '4'])
        
        if choice == '1':
            if not user.favorite_conversions:
                print("\nNo favorite conversions yet!")
                continue
                
            print("\nFavorite Conversions:")
            for conv in user.favorite_conversions:
                units = get_conversion_units(conv.conversion_type)
                print(f"  {conv.id}: {conv.input_value:.2f}{units[0]} → {conv.result_value:.2f}{units[1]}")
                
        elif choice == '2':
            if not user.conversions:
                print("No conversions to favorite yet!")
                continue
                
            print("\nAvailable Conversions:")
            for conv in user.conversions:
                if conv not in user.favorite_conversions:
                    units = get_conversion_units(conv.conversion_type)
                    print(f"  {conv.id}: {conv.input_value:.2f}{units[0]} → {conv.result_value:.2f}{units[1]}")
            
            conv_id = get_valid_int("\nEnter conversion ID to favorite: ")
            conversion = session.get(Conversion, conv_id)
            
            if not conversion:
                print("No conversion found with that ID")
                continue
                
            if conversion not in user.conversions:
                print("That conversion doesn't belong to this user")
                continue
                
            if user.add_favorite(session, conversion):
                print("Added to favorites!")
            else:
                print("This conversion is already in your favorites")
                
        elif choice == '3':
            if not user.favorite_conversions:
                print("No favorites to remove!")
                continue
                
            print("\nCurrent Favorites:")
            for conv in user.favorite_conversions:
                units = get_conversion_units(conv.conversion_type)
                print(f"  {conv.id}: {conv.input_value:.2f}{units[0]} → {conv.result_value:.2f}{units[1]}")
            
            conv_id = get_valid_int("\nEnter conversion ID to remove from favorites: ")
            conversion = session.get(Conversion, conv_id)
            
            if not conversion:
                print("No conversion found with that ID")
                continue
                
            if user.remove_favorite(session, conversion):
                print("Removed from favorites")
            else:
                print("This conversion wasn't in your favorites")
                
        elif choice == '4':
            break

def get_conversion_units(conv_type):
    return {
        'lbs_to_kg': ('lbs', 'kg'),
        'kg_to_lbs': ('kg', 'lbs'),
        'in_to_cm': ('inches', 'cm'),
        'cm_to_in': ('cm', 'inches')
    }.get(conv_type, ('?', '?'))

if __name__ == '__main__':
    print("Welcome to the Unit Converter!")
    main_menu()