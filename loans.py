"""Loans: US-06 issue a book, US-07 return a book."""

from datetime import date, timedelta
from storage import ask, available_copies, find_book, new_id, print_table, save_data
from members import find_member

LOAN_DAYS = 14
FINE_PER_DAY = 50


def ui_issue_book(db):
    print("\n--- Issue a book ---")
    book = find_book(db, ask("Book ID: "))
    if not book:
        print("Book not found.")
        return
    if available_copies(db, book) < 1:
        print("No copies currently available.")
        return

    member = find_member(db, ask("Member ID: "))
    if not member:
        print("Member not found.")
        return

    active = [
        l for l in db.get("loans", [])
        if l["member_id"] == member["id"] and not l.get("returned_date")
    ]
    if len(active) >= 3:
        print("Member already has the maximum of 3 active loans.")
        return

    today = date.today()
    loan = {
        "id": new_id(db.setdefault("loans", []), "L"),
        "book_id": book["id"],
        "member_id": member["id"],
        "issue_date": today.isoformat(),
        "due_date": (today + timedelta(days=LOAN_DAYS)).isoformat(),
        "returned_date": None,
    }
    db["loans"].append(loan)
    save_data(db)
    print(f"Issued '{book['title']}' to {member['name']} (Loan ID: {loan['id']}, Due: {loan['due_date']}).")


def ui_return_book(db):
    print("\n--- Return a book ---")
    loan_id = ask("Loan ID: ").strip().upper()
    loan = next((l for l in db.get("loans", []) if l["id"].upper() == loan_id), None)
    if not loan:
        print("Loan not found.")
        return
    if loan.get("returned_date"):
        print("This book has already been returned.")
        return

    today = date.today()
    due = date.fromisoformat(loan["due_date"])
    overdue_days = max(0, (today - due).days)
    fine = overdue_days * FINE_PER_DAY

    loan["returned_date"] = today.isoformat()
    loan["fine"] = fine
    save_data(db)
    print(f"Book returned. Overdue days: {overdue_days}, Fine: {fine}.")


def ui_list_loans(db):
    print("\n--- Active loans ---")
    headers = ["Loan ID", "Book ID", "Member ID", "Issue Date", "Due Date"]
    rows = [
        [l["id"], l["book_id"], l["member_id"], l["issue_date"], l["due_date"]]
        for l in db.get("loans", []) if not l.get("returned_date")
    ]
    print_table(headers, rows)