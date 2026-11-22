"""Dashboard: US-09 admin dashboard and reset sample data."""

from datetime import date
import os
from storage import available_copies, confirm, load_data


def ui_dashboard(db):
    print("\n--- Library Dashboard ---")
    books = db.get("books", [])
    members = db.get("members", [])
    loans = db.get("loans", [])
    total_copies = sum(b["copies"] for b in books)
    avail_copies = sum(available_copies(db, b) for b in books)
    active = [l for l in loans if not l.get("returned_on") and not l.get("returned_date")]
    overdue = [
        l for l in active
        if date.today() > date.fromisoformat(l.get("due_on") or l.get("due_date"))
    ]
    print(f"Total Titles   : {len(books)}")
    print(f"Total Copies   : {total_copies} (Available: {avail_copies})")
    print(f"Total Members  : {len(members)}")
    print(f"Active Loans   : {len(active)}")
    print(f"Overdue Loans  : {len(overdue)}")


def ui_reset(db):
    print("\n--- Reset sample data ---")
    if not confirm("Reset all data back to default sample data?"):
        return
    if os.path.exists("library_data.json"):
        os.remove("library_data.json")
    fresh = load_data()
    db.clear()
    db.update(fresh)
    print("Sample data has been reset.")