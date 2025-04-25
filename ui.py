"""
Author: Jason
E-mail: D23090120503@cityu.edu.mo
LastEditTime: 2025-04-25 13:35:42
"""

from tabulate import tabulate
import sys


def display_menu(title, options):
    """Displays a formatted menu."""
    print(f"\n--- {title} ---")
    for key, value in options.items():
        print(f"{key}. {value}")
    print("--------------------")


def get_choice(prompt="Enter your choice: "):
    """Gets user input for menu choice."""
    while True:
        try:
            choice = input(prompt).strip()
            if choice:  # Ensure input is not empty
                return choice
            else:
                print("Input cannot be empty.")
        except EOFError:
            print("\nExiting.")
            sys.exit(0)
        except KeyboardInterrupt:
            print("\nOperation cancelled. Returning to menu.")
            return None 


def get_input(prompt, required=True, input_type=str):
    """Gets user input with optional validation."""
    while True:
        try:
            value = input(f"{prompt}: ").strip()
            if not value and required:
                print("This field is required.")
                continue
            if value and input_type:
                try:
                    return input_type(value)
                except ValueError:
                    print(f"Invalid input. Please enter a valid {input_type.__name__}.")
                    continue
            return value  # Return even if empty if not required
        except EOFError:
            print("\nExiting.")
            sys.exit(0)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None


def display_table(data, headers="firstrow", title=None):
    """Displays data in a formatted table."""
    if not data:
        print("No data to display.")
        return

    if title:
        print(f"\n--- {title} ---")

    # If data is a list of dicts, extract headers and rows
    if isinstance(data, list) and data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        rows = [list(item.values()) for item in data]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    elif headers == "firstrow" and isinstance(data, list) and data:
        # Assumes first list is header, rest are data rows
        print(tabulate(data[1:], headers=data[0], tablefmt="grid"))
    else:
        # Fallback for simple lists or pre-formatted data
        print(tabulate(data, headers=headers, tablefmt="grid"))


def confirm_action(prompt="Are you sure you want to proceed? (yes/no): "):
    """Asks for confirmation before proceeding."""
    while True:
        choice = input(prompt).strip().lower()
        if choice == "yes":
            return True
        elif choice == "no":
            return False
        else:
            print("Please enter 'yes' or 'no'.")


def display_message(message, msg_type="info"):
    """Displays a formatted message (info, success, error)."""
    prefix = ""
    if msg_type == "success":
        prefix = "[SUCCESS] "
    elif msg_type == "error":
        prefix = "[ERROR] "
    elif msg_type == "warning":
        prefix = "[WARNING] "
    print(f"{prefix}{message}")
