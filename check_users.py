from app import app
from models import db, User

with app.app_context():
    users = User.query.all()
    print("--- User List ---")
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Role: '{u.role}', StudentID: '{u.student_id}', ChildReg: '{u.child_registration_number}'")
    print("-----------------")
