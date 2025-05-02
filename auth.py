
import bcrypt
import getpass  # For securely getting password input
from database import execute_query
from ui import display_message


def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(stored_password_hash, provided_password):
    """Verifies a provided password against a stored hash."""
    return bcrypt.checkpw(
        provided_password.encode("utf-8"), stored_password_hash.encode("utf-8")
    )


def register_user(
    username, password, role="reader", phone=None
):  # Added phone parameter
    """Registers a new user (typically called by an admin)."""
    if not username or not password:
        print("Username and password cannot be empty.")
        return False
    if role not in ["reader", "admin", "superadmin"]:
        print("Invalid role specified.")
        return False
    # Basic phone validation (optional)
    if phone and not phone.isdigit():
        print("Warning: Phone number should ideally contain only digits.", "warning")

    hashed_pw = hash_password(password)
    # Initialize permissions as empty string
    query = "INSERT INTO users (username, password_hash, role, phone, permissions) VALUES (%s, %s, %s, %s, %s)"
    try:
        user_id = execute_query(
            query,
            (username, hashed_pw.decode("utf-8"), role, phone, ""),
            commit=True,  
        )
        if user_id:
            print(f"User '{username}' registered successfully with ID: {user_id}")
            return True
        else:
            print(
                f"Failed to register user '{username}'. Username might already exist."
            )
            return False
    except Exception as e:
        print(f"An error occurred during registration: {e}")
        return False


def login_user():
    """Handles the user login process."""
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")  # Hides password input

    # Fetch permissions along with other user data
    query = "SELECT user_id, username, password_hash, role, permissions FROM users WHERE username = %s"
    user_data = execute_query(query, (username,), fetch_one=True)

    if user_data and verify_password(user_data["password_hash"], password):
        print(
            f"Login successful. Welcome, {user_data['username']} ({user_data['role']})!"
        )
        return {
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "role": user_data["role"],
            "permissions": user_data.get(
                "permissions", ""
            ),  # Ensure permissions key exists
        }
    else:
        return None


def create_initial_admin():
    """Guides the user through creating the initial 'admin' account."""
    print("\n--- Create Initial Superadmin Account ---")
    admin_user = "admin"
    admin_exists = execute_query(
        "SELECT 1 FROM users WHERE username = %s", (admin_user,), fetch_one=True
    )
    if admin_exists:
        display_message(f"User '{admin_user}' already exists.", "warning")
        return False

    while True:
        password = getpass.getpass(f"Enter password for '{admin_user}': ")
        if not password:
            display_message("Password cannot be empty.", "warning")
            continue
        confirm_pass = getpass.getpass("Confirm password: ")
        if password == confirm_pass:
            # Superadmin role implies all permissions, so the permissions string isn't strictly needed for checks
            if register_user(admin_user, password, "superadmin", phone=None):
                display_message(
                    f"Initial superadmin user '{admin_user}' created successfully.",
                    "success",
                )
                return True
            else:
                display_message(
                    f"Failed to create initial superadmin user '{admin_user}'.", "error"
                )
                return False
        else:
            display_message("Passwords do not match. Please try again.", "warning")


if __name__ == "__main__":
    print("Auth module direct execution (for setup/testing)")
    create_initial_admin()
