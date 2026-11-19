"""Books: US-01 add, US-02 list, US-03 edit and delete, US-04 search."""

import re
from storage import (
    ask,
    ask_int,
    available_copies,
    confirm,
    copies_on_loan,
    find_book,
    new_id,
    print_table,
    save_data,
)


# =========================================================
# US-01: Add a book  (validate_book is also used by US-03)
# =========================================================

def validate_book(db, title, author, isbn, copies, ignore_id=None):
    """Validate book fields and return an error message or None."""
    if not title or not title.strip():
        return "Title cannot be empty."
    if not author or not author.strip():
        return "Author cannot be empty."
    clean_isbn = re.sub(r"[-\s]", "", isbn or "")
    if not re.fullmatch(r"\d{10}|\d{13}", clean_isbn):
        return "ISBN must be 10 or 13 digits."
    for b in db["books"]:
        if b["id"] != ignore_id and re.sub(r"[-\s]", "", b["isbn"]) == clean_isbn:
            return f"ISBN already exists on book {b['id']}."
    if copies < 1:
        return "Copies must be at least 1."
    return None


def ui_add_book(db):
    """Prompt user for details and add a new book."""
    print("\n--- Add a book ---")
    title = ask("Title: ")
    author = ask("Author: ")
    isbn = ask("ISBN (10 or 13 digits): ")
    category = ask("Category (optional): ")
    copies = ask_int("Number of copies: ", min_val=1)
    if copies is None:
        return

    err = validate_book(db, title, author, isbn, copies)
    if err:
        print(f"Error: {err}")
        return

    book = {
        "id": new_id(db["books"], "B"),
        "title": title.strip(),
        "author": author.strip(),
        "isbn": isbn.strip(),
        "category": category.strip(),
        "copies": copies,
    }
    db["books"].append(book)
    save_data(db)
    print(f"Added '{book['title']}' with ID {book['id']}.")


# =========================================================
# US-02: List all books
# =========================================================

def book_rows(db, books):
    """Prepare book information for displaying in a table."""
    return [
        [
            b["id"],
            b["title"],
            b["author"],
            b["isbn"],
            b["category"] or "-",
            f'{available_copies(db, b)} / {b["copies"]}',
        ]
        for b in books
    ]


BOOK_HEADERS = ["ID", "Title", "Author", "ISBN", "Category", "Available / Total"]


def ui_list_books(db):
    """Display all books, sorted alphabetically by title."""
    print("\n--- All books ---")
    books = sorted(db["books"], key=lambda b: b["title"].lower())
    print_table(BOOK_HEADERS, book_rows(db, books))


# =========================================================
# US-03: Edit and delete a book
# =========================================================

def ui_edit_book(db):
    """Edit an existing book's details."""
    print("\n--- Edit a book ---")
    book = find_book(db, ask("Book ID to edit: "))
    if not book:
        print("Book not found.")
        return

    print("Press Enter to keep the current value.")
    title = ask(f"Title [{book['title']}]: ") or book["title"]
    author = ask(f"Author [{book['author']}]: ") or book["author"]
    isbn = ask(f"ISBN [{book['isbn']}]: ") or book["isbn"]
    category_in = ask(f"Category [{book['category'] or '-'}]: ")
    category = book["category"] if category_in == "" else category_in

    copies_raw = ask(f"Copies [{book['copies']}]: ")
    if copies_raw == "":
        copies = book["copies"]
    elif copies_raw.isdigit():
        copies = int(copies_raw)
    else:
        print("Copies must be a whole number.")
        return

    on_loan = copies_on_loan(db, book["id"])
    if copies < on_loan:
        print(f"Cannot set copies below currently loaned count ({on_loan}).")
        return

    err = validate_book(db, title, author, isbn, copies, ignore_id=book["id"])
    if err:
        print(f"Error: {err}")
        return

    book.update({
        "title": title.strip(),
        "author": author.strip(),
        "isbn": isbn.strip(),
        "category": category.strip(),
        "copies": copies,
    })
    save_data(db)
    print(f"Updated '{book['title']}' ({book['id']}).")


def ui_delete_book(db):
    """Delete a book if no copies are currently on loan."""
    print("\n--- Delete a book ---")
    book = find_book(db, ask("Book ID to delete: "))
    if not book:
        print("Book not found.")
        return

    if copies_on_loan(db, book["id"]) > 0:
        print("Cannot delete: one or more copies are currently on loan.")
        return

    if confirm(f"Delete '{book['title']}' ({book['id']})?"):
        db["books"].remove(book)
        save_data(db)
        print("Book deleted.")


# =========================================================
# US-04: Search books
# =========================================================

def ui_search_books(db):
    """Search books by title, author, ISBN, or category."""
    print("\n--- Search books ---")
    query = ask("Search term (title, author, ISBN, or category): ").strip().lower()
    if not query:
        print("Search term cannot be empty.")
        return

    matches = [
        b for b in db["books"]
        if query in b["title"].lower()
        or query in b["author"].lower()
        or query in b["isbn"].lower()
        or query in (b["category"] or "").lower()
    ]
    if not matches:
        print("No matching books found.")
        return

    matches = sorted(matches, key=lambda b: b["title"].lower())
    print_table(BOOK_HEADERS, book_rows(db, matches))