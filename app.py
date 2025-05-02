import sys
import operations
import reports
from ui import display_menu, get_choice, display_message
from auth import login_user, create_initial_admin
from database import test_connection, execute_query


def reader_menu(user):
    """Displays the menu for reader users."""
    options = {
        "1": "Search Books",
        "2": "List All Books",
        "3": "Borrow Book",
        "4": "Return Book",
        "5": "View My Loans",
        "0": "Logout",
    }
    while True:
        display_menu(f"Reader Menu (User: {user['username']})", options)
        choice = get_choice()
        if choice == "1":
            operations.search_books()
        elif choice == "2":
            operations.list_all_books()
        elif choice == "3":
            operations.borrow_book(user["user_id"])
        elif choice == "4":
            operations.return_book(user["user_id"])
        elif choice == "5":
            operations.list_user_loans(user["user_id"])
        elif choice == "0":
            display_message("Logging out.", "info")
            break
        elif choice is None:  
            continue
        else:
            display_message("Invalid choice, please try again.", "warning")


def admin_menu(user):
    """Displays the menu for admin users."""
    options = {
        # Book Management
        "1": "Search Books",
        "2": "List All Books",
        "3": "Add New Book",
        "4": "Update Book Details",
        "5": "Delete Book",
        # Loan Management
        "6": "List All Loans (History)",
        "7": "List Active Loans",
        # User Management
        "8": "List Users",
        "9": "Add New User",
        "10": "Update User",
        "11": "Delete User",
        # Reports
        "12": "View Statistics",
        "0": "Logout",
    }
    while True:
        display_menu(f"Admin Menu (User: {user['username']})", options)
        choice = get_choice()
        if choice == "1":
            operations.search_books()
        elif choice == "2":
            operations.list_all_books()
        elif choice == "3":
            operations.add_book(user) 
        elif choice == "4":
            operations.update_book(user)
        elif choice == "5":
            operations.delete_book(user)
        elif choice == "6":
            operations.list_all_loans(user, only_active=False)  
        elif choice == "7":
            operations.list_all_loans(user, only_active=True)  
        elif choice == "8":
            operations.list_users(user)  
        elif choice == "9":
            operations.add_user(user)
        elif choice == "10":
            operations.update_user(user)
        elif choice == "11":
            operations.delete_user(user)
        elif choice == "12":
            reports.display_statistics()
        elif choice == "0":
            display_message("Logging out.", "info")
            break
        elif choice is None:  
            continue
        else:
            display_message("Invalid choice, please try again.", "warning")


def superadmin_menu(user):
    """Displays the menu for superadmin users."""
    options = {
        # Book Management
        "1": "Search Books",
        "2": "List All Books",
        "3": "Add New Book",
        "4": "Update Book Details",
        "5": "Delete Book",
        # Loan Management
        "6": "List All Loans (History)",
        "7": "List Active Loans",
        # User Management
        "8": "List Users",
        "9": "Add New User",
        "10": "Update User",
        "11": "Delete User",
        # Reports
        "12": "View Statistics",
        # Role Management
        "13": "Manage User Roles & Permissions",
        "0": "Logout",
    }
    while True:
        display_menu(f"Superadmin Menu (User: {user['username']})", options)
        choice = get_choice()
        if choice == "1":
            operations.search_books()
        elif choice == "2":
            operations.list_all_books()
        elif choice == "3":
            operations.add_book(user)  
        elif choice == "4":
            operations.update_book(user)
        elif choice == "5":
            operations.delete_book(user)
        elif choice == "6":
            operations.list_all_loans(user, only_active=False)  
        elif choice == "7":
            operations.list_all_loans(user, only_active=True)  
        elif choice == "8":
            operations.list_users(user)  
        elif choice == "9":
            operations.add_user(user)
        elif choice == "10":
            operations.update_user(user)
        elif choice == "11":
            operations.delete_user(user)
        elif choice == "12":
            reports.display_statistics()
        elif choice == "13":
            operations.assign_role_permissions(user) 
        elif choice == "0":
            display_message("Logging out.", "info")
            break
        elif choice is None:
            continue
        else:
            display_message("Invalid choice, please try again.", "warning")


def main():
    """Main function"""
    print("Welcome to the Library Management System!")

    if not test_connection():
        display_message(
            "Critical error: Cannot connect to the database. Exiting.", "error"
        )
        sys.exit(1)

    while True:
        # Display login/exit options before prompting for credentials
        login_options = {"1": "Login", "0": "Exit System"}
        display_menu("Main Menu", login_options)
        choice = get_choice()

        if choice == "0":
            break

        elif choice == "1":
            print("\nPlease login to continue.")
            user = login_user() #  returns permissions

            if user:
                role = user["role"]
                permissions_str = user.get("permissions", "") # Get permissions 

                print(f"\nLogin successful. Welcome, {user['username']}!")
                print(f"Your role: {role.capitalize()}")

                # Display specific permissions if they exist
                if permissions_str:
                    print("You have the following specific permissions:")
                    permissions_list = [p.strip() for p in permissions_str.split(',') if p.strip()]
                    if permissions_list:
                        for perm in permissions_list:
                            print(f"- {perm.capitalize()}")
                    else:
                         print("- None specified (using default role permissions).")
                else:
                    print("No specific permissions assigned; using default role permissions.")

 # Call the appropriate menu based on role
                if role == "superadmin":
                    superadmin_menu(user)
                elif role == "admin":
                    admin_menu(user)
                elif role == "reader":
                    reader_menu(user)
                else:
                    display_message(
                        f"Unknown user role: {role}. Logging out.", "error"
                    )
            else:
                
                admin_exists = execute_query(
                    "SELECT 1 FROM users WHERE username = %s",
                    ("admin",),
                    fetch_one=True,
                )

                if not admin_exists:
                    # Admin doesn't exist, offer to create
                    create = get_choice(
                        "Login failed. Initial admin user not found. Create it now? (yes/no): "
                    ).lower()
                    if create == "yes":
                        if create_initial_admin():
                            display_message(
                                "Admin account created. Please login again.", "info"
                            )
                        else:
                            display_message("Admin creation failed. Exiting.", "error")
                            break  
                        continue  
                    else:
                        display_message(
                            "Cannot proceed without admin account. Exiting.", "info"
                        )
                        break  
                else:
                    # Admin exists, login just failed for other reasons
                    display_message("Invalid username or password.", "error")
                    retry = get_choice("Try again? (yes/no): ").lower()
                    if retry != "yes":
                        break  

        else:
            display_message("Invalid choice, please try again.", "warning")


    print("\nThank you for using the Library Management System. Goodbye!")


if __name__ == "__main__":
    main()
