"""Usage: python create_admin.py  (prompts for details) - creates or promotes a faculty admin."""
import getpass
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    name = input("Name: "); roll = input("ID/Roll: "); email = input("Email: ").lower()
    pw = getpass.getpass("Password (min 8): ")
    u = User.query.filter_by(email=email).first() or User(email=email)
    u.name, u.roll_number, u.role = name, roll, "admin"; u.set_password(pw)
    db.session.add(u); db.session.commit(); print("Admin ready.")
