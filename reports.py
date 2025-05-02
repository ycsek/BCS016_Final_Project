from database import execute_query
from ui import display_message
import matplotlib.pyplot as plt


def display_statistics():
    print("\n--- Library Statistics ---")
    # --- Database Queries ---
    total_books_query = "SELECT COUNT(*) as count FROM books"
    total_books_result = execute_query(total_books_query, fetch_one=True)
    total_books = total_books_result["count"] if total_books_result else 0

    total_copies_query = "SELECT SUM(quantity) as total_copies FROM books"
    total_copies_result = execute_query(total_copies_query, fetch_one=True)
    total_copies = (
        total_copies_result["total_copies"]
        if total_copies_result and total_copies_result["total_copies"] is not None
        else 0
    )

    active_loans_query = "SELECT COUNT(*) as count FROM loans WHERE return_date IS NULL"
    active_loans_result = execute_query(active_loans_query, fetch_one=True)
    active_loans = active_loans_result["count"] if active_loans_result else 0

    total_users_query = "SELECT COUNT(*) as count FROM users"
    total_users_result = execute_query(total_users_query, fetch_one=True)
    total_users = total_users_result["count"] if total_users_result else 0

    # --- Visualization ---
    labels = ["Total books", "Total Copies", "Active Loans", "Total Users"]
    values = [total_books, total_copies, active_loans, total_users]

    try:
        plt.figure(figsize=(8, 4))
        bars = plt.bar(labels, values, color=["blue", "green", "red", "purple"])
        plt.ylabel("Count")
        plt.title("Library Statistics Overview")

        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                yval,
                int(yval),
                va="bottom",
                ha="center",
            )

        plt.tight_layout()
        plt.show()  # Display the plot
        display_message("Statistics chart displayed.", "info")
    except Exception as e:
        display_message(f"Error generating plot: {e}", "error")
        # Print basic info if plot fails, but not as a full fallback
        print(
            f"Data: Titles={total_books}, Copies={total_copies}, Loans={active_loans}, Users={total_users}"
        )
