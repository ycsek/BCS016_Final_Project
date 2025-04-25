"""
Author: Jason
E-mail: D23090120503@cityu.edu.mo
LastEditTime: 2025-04-25 13:31:51
"""

from database import execute_query
from ui import get_input, display_table, confirm_action, display_message
from datetime import date, timedelta
from auth import register_user

# --- Book Operations ---


def add_book():
    """Adds a new book to the database."""
    print("\n--- Add New Book ---")
    title = get_input("Enter title", required=True)
    if title is None:
        return  # User cancelled
    author = get_input("Enter author", required=True)
    if author is None:
        return
    isbn = get_input("Enter ISBN (optional)", required=False)
    if isbn is None:
        return
    quantity = get_input("Enter quantity", required=True, input_type=int)
    if quantity is None or quantity <= 0:
        display_message("Quantity must be a positive integer.", "error")
        return

    query_check = "SELECT book_id FROM books WHERE title = %s AND author = %s"
    existing = execute_query(query_check, (title, author), fetch_one=True)
    if existing:
        display_message(
            f"A book with title '{title}' by '{author}' already exists (ID: {existing['book_id']}). Use update instead.",
            "warning",
        )
        return

    query = """
        INSERT INTO books (title, author, isbn, quantity, available_quantity)
        VALUES (%s, %s, %s, %s, %s)
    """
    book_id = execute_query(
        query, (title, author, isbn, quantity, quantity), commit=True
    )

    if book_id:
        display_message(
            f"Book '{title}' added successfully with ID: {book_id}", "success"
        )
    else:
        display_message("Failed to add book.", "error")


def update_book():
    """Updates an existing book's details."""
    print("\n--- Update Book ---")
    book_id = get_input(
        "Enter the ID of the book to update", required=True, input_type=int
    )
    if book_id is None:
        return

    # Fetch current details
    current_book = execute_query(
        "SELECT * FROM books WHERE book_id = %s", (book_id,), fetch_one=True
    )
    if not current_book:
        display_message(f"Book with ID {book_id} not found.", "error")
        return

    display_message("Current details:")
    display_table([current_book])

    title = (
        get_input(
            f"Enter new title (leave blank to keep '{current_book['title']}')",
            required=False,
        )
        or current_book["title"]
    )
    author = (
        get_input(
            f"Enter new author (leave blank to keep '{current_book['author']}')",
            required=False,
        )
        or current_book["author"]
    )
    isbn = (
        get_input(
            f"Enter new ISBN (leave blank to keep '{current_book['isbn']}')",
            required=False,
        )
        or current_book["isbn"]
    )
    quantity_str = get_input(
        f"Enter new total quantity (leave blank to keep '{current_book['quantity']}')",
        required=False,
    )

    new_quantity = current_book["quantity"]
    if quantity_str:
        try:
            new_quantity = int(quantity_str)
            if new_quantity < 0:
                display_message("Quantity cannot be negative.", "error")
                return
        except ValueError:
            display_message("Invalid quantity entered. Keeping original.", "warning")
            new_quantity = current_book["quantity"]

    # Calculate change in quantity to adjust available quantity
    quantity_change = new_quantity - current_book["quantity"]
    new_available_quantity = current_book["available_quantity"] + quantity_change

    # Ensure available quantity doesn't exceed total quantity or become negative
    if new_available_quantity < 0:
        display_message(
            "Cannot reduce total quantity below the number of currently loaned books.",
            "error",
        )
        return
    if new_available_quantity > new_quantity:
        new_available_quantity = (
            new_quantity  # Should not happen with logic above, but safety check
        )

    query = """
        UPDATE books
        SET title = %s, author = %s, isbn = %s, quantity = %s, available_quantity = %s
        WHERE book_id = %s
    """
    params = (title, author, isbn, new_quantity, new_available_quantity, book_id)

    if confirm_action(f"Update book ID {book_id}?"):
        rows_affected = execute_query(query, params, commit=True)
        display_message(f"Book ID {book_id} updated successfully.", "success")
        # Re-fetch and display updated details
        updated_book = execute_query(
            "SELECT * FROM books WHERE book_id = %s", (book_id,), fetch_one=True
        )
        if updated_book:
            display_table([updated_book])

    else:
        display_message("Update cancelled.", "info")


def delete_book():
    """Deletes a book from the database."""
    print("\n--- Delete Book ---")
    book_id = get_input(
        "Enter the ID of the book to delete", required=True, input_type=int
    )
    if book_id is None:
        return

    # Check if book exists
    book = execute_query(
        "SELECT title, author, available_quantity, quantity FROM books WHERE book_id = %s",
        (book_id,),
        fetch_one=True,
    )
    if not book:
        display_message(f"Book with ID {book_id} not found.", "error")
        return

    # Check for active loans
    if book["available_quantity"] < book["quantity"]:
        display_message(
            f"Cannot delete book '{book['title']}' as it has active loans.", "error"
        )
        return

    if confirm_action(
        f"Delete book '{book['title']}' by {book['author']} (ID: {book_id})? This is irreversible."
    ):
        query = "DELETE FROM books WHERE book_id = %s"
        # Assuming execute_query handles commit correctly
        execute_query(query, (book_id,), commit=True)
        # Check if deletion was successful (ideally check row count)
        check_deleted = execute_query(
            "SELECT 1 FROM books WHERE book_id = %s", (book_id,), fetch_one=True
        )
        if not check_deleted:
            display_message(f"Book ID {book_id} deleted successfully.", "success")
        else:
            display_message(f"Failed to delete book ID {book_id}.", "error")

    else:
        display_message("Deletion cancelled.", "info")


def search_books():
    """Searches for books based on multiple criteria (title, author, ISBN) using LIKE."""
    print("\n--- Search Books ---")
    title_query = get_input(
        "Enter title fragment (leave blank if not searching by title)", required=False
    )
    author_query = get_input(
        "Enter author fragment (leave blank if not searching by author)", required=False
    )
    isbn_query = get_input(
        "Enter ISBN fragment (leave blank if not searching by ISBN)", required=False
    )

    conditions = []
    params = []

    if title_query:
        conditions.append("title LIKE %s")
        params.append(f"%{title_query}%")
    if author_query:
        conditions.append("author LIKE %s")
        params.append(f"%{author_query}%")
    if isbn_query:
        conditions.append("isbn LIKE %s")
        params.append(f"%{isbn_query}%")

    if not conditions:
        display_message("Please provide at least one search criterion.", "warning")
        list_all_books()  # Show all if no criteria given
        return

    base_query = (
        "SELECT book_id, title, author, isbn, quantity, available_quantity FROM books"
    )
    where_clause = " WHERE " + " AND ".join(conditions)
    query = base_query + where_clause + " ORDER BY title"

    results = execute_query(query, tuple(params), fetch_all=True)

    if results:
        display_table(results, title="Search Results")
    else:
        display_message("No books found matching your criteria.", "info")


def list_all_books():
    """Lists all books in the database."""
    print("\n--- All Books ---")
    query = "SELECT book_id, title, author, isbn, quantity, available_quantity FROM books ORDER BY title"
    books = execute_query(query, fetch_all=True)
    display_table(books, title="Library Catalog")


# --- Loan Operations ---


def borrow_book(user_id):
    """Allows a user to borrow a book."""
    print("\n--- Borrow Book ---")
    book_id = get_input(
        "Enter the ID of the book to borrow", required=True, input_type=int
    )
    if book_id is None:
        return

    # Check if book exists and is available
    book = execute_query(
        "SELECT available_quantity FROM books WHERE book_id = %s",
        (book_id,),
        fetch_one=True,
    )
    if not book:
        display_message(f"Book with ID {book_id} not found.", "error")
        return
    if book["available_quantity"] <= 0:
        display_message(
            "Sorry, this book is currently unavailable (all copies loaned out).", "info"
        )
        return

    # Check if user already has this book loaned out (and not returned)
    existing_loan = execute_query(
        "SELECT loan_id FROM loans WHERE user_id = %s AND book_id = %s AND return_date IS NULL",
        (user_id, book_id),
        fetch_one=True,
    )
    if existing_loan:
        display_message("You already have this book borrowed.", "warning")
        return

    loan_date = date.today()
    due_date = loan_date + timedelta(days=14)  # Example: 2-week loan period

    loan_query = """
        INSERT INTO loans (user_id, book_id, loan_date, due_date)
        VALUES (%s, %s, %s, %s)
    """
    update_book_query = """
        UPDATE books SET available_quantity = available_quantity - 1
        WHERE book_id = %s AND available_quantity > 0
    """


    loan_id = execute_query(
        loan_query, (user_id, book_id, loan_date, due_date), commit=True
    )

    if loan_id:
        rows_affected = execute_query(update_book_query, (book_id,), commit=True)
        display_message(
            f"Book ID {book_id} borrowed successfully. Due date: {due_date}", "success"
        )
    else:
        display_message("Failed to record loan.", "error")
        # Ideally, rollback the book quantity update if the loan insert failed (needs proper transaction mgmt)


def return_book(user_id):
    """Allows a user to return a borrowed book."""
    print("\n--- Return Book ---")
    list_user_loans(user_id, only_active=True)  # Show active loans first

    loan_id = get_input(
        "Enter the ID of the loan to return", required=True, input_type=int
    )
    if loan_id is None:
        return

    # Verify the loan exists, belongs to the user, and is not already returned
    loan_details = execute_query(
        "SELECT loan_id, book_id FROM loans WHERE loan_id = %s AND user_id = %s AND return_date IS NULL",
        (loan_id, user_id),
        fetch_one=True,
    )

    if not loan_details:
        display_message(
            f"Active loan with ID {loan_id} not found for your account.", "error"
        )
        return

    book_id = loan_details["book_id"]
    return_date = date.today()

    return_query = "UPDATE loans SET return_date = %s WHERE loan_id = %s"
    update_book_query = "UPDATE books SET available_quantity = available_quantity + 1 WHERE book_id = %s"

    rows_affected_loan = execute_query(
        return_query, (return_date, loan_id), commit=True
    )
    # Check success based on no error

    display_message(f"Processing return for loan ID {loan_id}...", "info")

    # Update book availability
    rows_affected_book = execute_query(update_book_query, (book_id,), commit=True)
    # Check success based on no error

    display_message(f"Book (from loan ID {loan_id}) returned successfully.", "success")


def list_user_loans(user_id, only_active=False):
    """Lists loans for the current user."""
    print("\n--- Your Loans ---")
    query = """
        SELECT l.loan_id, b.title, b.author, l.loan_date, l.due_date, l.return_date
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        WHERE l.user_id = %s
    """
    params = [user_id]
    if only_active:
        query += " AND l.return_date IS NULL"

    query += " ORDER BY l.loan_date DESC"

    loans = execute_query(query, tuple(params), fetch_all=True)
    if loans:
        title = "Your Active Loans" if only_active else "Your Loan History"
        # Format dates for better display
        for loan in loans:
            loan["loan_date"] = (
                loan["loan_date"].strftime("%Y-%m-%d")
                if loan.get("loan_date")
                else "N/A"
            )
            loan["due_date"] = (
                loan["due_date"].strftime("%Y-%m-%d") if loan.get("due_date") else "N/A"
            )
            loan["return_date"] = (
                loan["return_date"].strftime("%Y-%m-%d")
                if loan.get("return_date")
                else "Not Returned"
            )
        display_table(loans, title=title)
    else:
        status = "active" if only_active else ""
        display_message(f"You have no {status} loans.", "info")


# --- Admin Only Operations ---


def list_all_loans(only_active=False):
    """Lists all loans (Admin only)."""
    print("\n--- All Library Loans ---")
    query = """
        SELECT l.loan_id, u.username, b.title, l.loan_date, l.due_date, l.return_date
        FROM loans l
        JOIN users u ON l.user_id = u.user_id
        JOIN books b ON l.book_id = b.book_id
    """
    if only_active:
        query += " WHERE l.return_date IS NULL"

    query += " ORDER BY l.loan_date DESC"

    loans = execute_query(query, fetch_all=True)
    if loans:
        title = "All Active Loans" if only_active else "All Loan History"
        # Format dates
        for loan in loans:
            loan["loan_date"] = (
                loan["loan_date"].strftime("%Y-%m-%d")
                if loan.get("loan_date")
                else "N/A"
            )
            loan["due_date"] = (
                loan["due_date"].strftime("%Y-%m-%d") if loan.get("due_date") else "N/A"
            )
            loan["return_date"] = (
                loan["return_date"].strftime("%Y-%m-%d")
                if loan.get("return_date")
                else "Not Returned"
            )
        display_table(loans, title=title)
    else:
        status = "active" if only_active else ""
        display_message(f"There are no {status} loans in the system.", "info")


def add_user():
    """Adds a new user (Admin only)."""

    print("\n--- Add New User ---")
    username = get_input("Enter username for new user", required=True)
    if username is None:
        return
    password = get_input(
        "Enter password for new user", required=True
    )  # Consider using getpass
    if password is None:
        return
    role = get_input("Enter role ('reader' or 'admin')", required=True).lower()
    if role not in ["reader", "admin"]:
        display_message("Invalid role. Must be 'reader' or 'admin'.", "error")
        return
    # Get phone number (optional)
    phone = get_input("Enter phone number (optional)", required=False)
    if (
        phone is None and phone != ""
    ):
        return  # User cancelled during phone input

    register_user(
        username, password, role, phone if phone else None
    )  # Pass None if empty string


def list_users():
    """Lists all users (Admin only)."""
    print("\n--- All Users ---")
    # Updated query to select phone
    query = (
        "SELECT user_id, username, role, phone, created_at FROM users ORDER BY username"
    )
    users = execute_query(query, fetch_all=True)
    if users:
        for user in users:
            user["created_at"] = (
                user["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                if user.get("created_at")
                else "N/A"
            )
            # Ensure phone is displayed nicely if it's NULL/None in DB
            user["phone"] = user.get("phone") or "N/A"
        display_table(users, title="User Accounts")
    else:
        display_message("No users found in the system.", "info")


def update_user():
    """Updates an existing user's details (Admin only)."""
    print("\n--- Update User ---")
    user_id = get_input(
        "Enter the ID of the user to update", required=True, input_type=int
    )
    if user_id is None:
        return

    # Fetch current details
    current_user = execute_query(
        "SELECT user_id, username, role, phone FROM users WHERE user_id = %s",
        (user_id,),
        fetch_one=True,
    )
    if not current_user:
        display_message(f"User with ID {user_id} not found.", "error")
        return

    display_message("Current details:")
    display_table([current_user])

    username = (
        get_input(
            f"Enter new username (leave blank to keep '{current_user['username']}')",
            required=False,
        )
        or current_user["username"]
    )
    role_input = get_input(
        f"Enter new role ('reader' or 'admin', leave blank to keep '{current_user['role']}')",
        required=False,
    )
    role = role_input.lower() if role_input else current_user["role"]
    if role not in ["reader", "admin"]:
        display_message("Invalid role. Must be 'reader' or 'admin'.", "error")
        return

    phone_input = get_input(
        f"Enter new phone (leave blank to keep '{current_user.get('phone') or 'N/A'}')",
        required=False,
    )
    if phone_input is None:
        return
    new_phone = phone_input or current_user.get("phone")

    if confirm_action(f"Update user ID {user_id}?"):
        query = """
            UPDATE users
            SET username = %s, role = %s, phone = %s
            WHERE user_id = %s
        """
        execute_query(query, (username, role, new_phone, user_id), commit=True)
        display_message(f"User ID {user_id} updated successfully.", "success")
        # Re-fetch and display updated details
        updated_user = execute_query(
            "SELECT user_id, username, role, phone, created_at FROM users WHERE user_id = %s",
            (user_id,),
            fetch_one=True,
        )
        if updated_user:
            updated_user["created_at"] = updated_user["created_at"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            updated_user["phone"] = updated_user.get("phone") or "N/A"
            display_table([updated_user])
    else:
        display_message("Update cancelled.", "info")


def delete_user():
    """Deletes a user (Admin only)."""
    print("\n--- Delete User ---")
    user_id = get_input(
        "Enter the ID of the user to delete", required=True, input_type=int
    )
    if user_id is None:
        return

    # Fetch user
    user = execute_query(
        "SELECT username FROM users WHERE user_id = %s", (user_id,), fetch_one=True
    )
    if not user:
        display_message(f"User with ID {user_id} not found.", "error")
        return

    # Check for active loans
    active_loan = execute_query(
        "SELECT 1 FROM loans WHERE user_id = %s AND return_date IS NULL",
        (user_id,),
        fetch_one=True,
    )
    if active_loan:
        display_message("Cannot delete user with active loans.", "error")
        return

    if confirm_action(
        f"Delete user '{user['username']}' (ID: {user_id})? This is irreversible."
    ):
        execute_query("DELETE FROM users WHERE user_id = %s", (user_id,), commit=True)
        # Verify deletion
        check_deleted = execute_query(
            "SELECT 1 FROM users WHERE user_id = %s", (user_id,), fetch_one=True
        )
        if not check_deleted:
            display_message(f"User ID {user_id} deleted successfully.", "success")
        else:
            display_message(f"Failed to delete user ID {user_id}.", "error")
    else:
        display_message("Deletion cancelled.", "info")
