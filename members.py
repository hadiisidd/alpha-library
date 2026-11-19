"""Members: US-05 register and remove members."""

import re
from storage import ask, confirm, new_id, print_table, save_data


def find_member(db, member_id):
    mid = (member_id or "").strip().upper()
    return next((m for m in db.get("members", []) if m["id"].upper() == mid), None)


def ui_list_members(db):
    print("\n--- All members ---")
    headers = ["ID", "Name", "Email", "Phone"]
    rows = [[m["id"], m["name"], m["email"], m.get("phone") or "-"] for m in db.get("members", [])]
    print_table(headers, rows)


def ui_register_member(db):
    print("\n--- Register member ---")
    name = ask("Full name: ").strip()
    email = ask("Email: ").strip()
    phone = ask("Phone (optional): ").strip()

    if not name:
        print("Name cannot be empty.")
        return
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        print("Invalid email address.")
        return
    if any(m["email"].lower() == email.lower() for m in db.get("members", [])):
        print("A member with that email already exists.")
        return

    member = {
        "id": new_id(db.setdefault("members", []), "M"),
        "name": name,
        "email": email,
        "phone": phone,
    }
    db["members"].append(member)
    save_data(db)
    print(f"Registered member {member['name']} with ID {member['id']}.")


def ui_remove_member(db):
    print("\n--- Remove member ---")
    member = find_member(db, ask("Member ID to remove: "))
    if not member:
        print("Member not found.")
        return

    active_loans = [
        l for l in db.get("loans", [])
        if l["member_id"] == member["id"] and not l.get("returned_date")
    ]
    if active_loans:
        print("Cannot remove member with active loans.")
        return

    if confirm(f"Remove member '{member['name']}' ({member['id']})?"):
        db["members"].remove(member)
        save_data(db)
        print("Member removed.")