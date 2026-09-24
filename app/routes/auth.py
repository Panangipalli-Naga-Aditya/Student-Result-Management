import re
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User

bp = Blueprint("auth", __name__, url_prefix="/api")

@bp.post("/auth/register")
def register():
    d = request.get_json(silent=True) or {}
    name, roll, email = (d.get(k, "").strip() for k in ("name", "roll_number", "email"))
    pw = d.get("password", "")
    if not (name and roll and email and pw): return jsonify(error="All fields are required."), 400
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email): return jsonify(error="Invalid email address."), 400
    if len(pw) < 8: return jsonify(error="Password must be at least 8 characters."), 400
    if pw != d.get("confirm_password"): return jsonify(error="Passwords do not match."), 400
    if User.query.filter((User.email == email.lower()) | (User.roll_number == roll)).first():
        return jsonify(error="Email or roll number already registered."), 409
    u = User(name=name, roll_number=roll, email=email.lower()); u.set_password(pw)
    db.session.add(u); db.session.commit(); login_user(u)
    return jsonify(user=u.to_dict()), 201

@bp.post("/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    ident = d.get("identifier", "").strip()
    u = User.query.filter((User.email == ident.lower()) | (User.roll_number == ident)).first()
    if not u or not u.check_password(d.get("password", "")): return jsonify(error="Invalid credentials."), 401
    login_user(u); return jsonify(user=u.to_dict())

@bp.post("/auth/logout")
@login_required
def logout(): logout_user(); return jsonify(ok=True)

@bp.get("/auth/me")
def me(): return jsonify(user=current_user.to_dict() if current_user.is_authenticated else None)
