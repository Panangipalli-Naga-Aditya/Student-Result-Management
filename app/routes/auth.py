import re
from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User

bp = Blueprint("auth", __name__, url_prefix="/api")


def _login_response(u):
    # remember=True keeps the login across browser restarts for the configured duration.
    login_user(u, remember=True, duration=timedelta(days=30), fresh=True)
    return jsonify(user=u.to_dict())


@bp.post("/auth/register")
def register():
    d = request.get_json(silent=True) or {}
    name, roll, email = (d.get(k, "").strip() for k in ("name", "roll_number", "email"))
    pw = d.get("password", "")
    if not (name and roll and email and pw):
        return jsonify(error="All fields are required."), 400
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify(error="Invalid email address."), 400
    if len(pw) < 8:
        return jsonify(error="Password must be at least 8 characters."), 400
    if pw != d.get("confirm_password"):
        return jsonify(error="Passwords do not match."), 400
    if User.query.filter((User.email == email.lower()) | (User.roll_number == roll)).first():
        return jsonify(error="Email or roll number already registered. Please log in instead."), 409

    u = User(name=name, roll_number=roll, email=email.lower(), role="student")
    u.set_password(pw)
    db.session.add(u)
    db.session.commit()
    return _login_response(u), 201


@bp.post("/auth/teacher-register")
def teacher_register():
    """Create a new teacher account with administrator privileges."""
    d = request.get_json(silent=True) or {}
    name, teacher_id, email = (
        d.get(k, "").strip() for k in ("name", "teacher_id", "email")
    )
    pw = d.get("password", "")

    if not (name and teacher_id and email and pw):
        return jsonify(error="All fields are required."), 400
    if not re.match(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", email):
        return jsonify(error="Invalid email address."), 400
    if len(pw) < 8:
        return jsonify(error="Password must be at least 8 characters."), 400
    if pw != d.get("confirm_password"):
        return jsonify(error="Passwords do not match."), 400

    # Teacher IDs share the same unique identifier column as student roll numbers,
    # so one ID cannot accidentally belong to two accounts.
    if User.query.filter(
        (User.email == email.lower()) | (User.roll_number == teacher_id)
    ).first():
        return jsonify(error="Email or Teacher ID already registered. Please log in instead."), 409

    u = User(
        name=name,
        roll_number=teacher_id,
        email=email.lower(),
        role="admin",
    )
    u.set_password(pw)
    db.session.add(u)
    db.session.commit()
    return _login_response(u), 201


@bp.post("/auth/student-login")
def student_login():
    d = request.get_json(silent=True) or {}
    ident = d.get("identifier", "").strip()
    u = User.query.filter((User.email == ident.lower()) | (User.roll_number == ident)).first()
    if not u or not u.check_password(d.get("password", "")) or u.role != "student":
        return jsonify(error="Invalid student credentials."), 401
    return _login_response(u)


@bp.post("/auth/teacher-login")
def teacher_login():
    d = request.get_json(silent=True) or {}
    ident = d.get("identifier", "").strip()
    u = User.query.filter((User.email == ident.lower()) | (User.roll_number == ident)).first()
    if not u or not u.check_password(d.get("password", "")) or not u.is_admin:
        return jsonify(error="Invalid teacher/admin credentials."), 401
    return _login_response(u)


# Backwards-compatible endpoint for existing clients.
@bp.post("/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    ident = d.get("identifier", "").strip()
    u = User.query.filter((User.email == ident.lower()) | (User.roll_number == ident)).first()
    if not u or not u.check_password(d.get("password", "")):
        return jsonify(error="Invalid credentials."), 401
    return _login_response(u)


@bp.post("/auth/logout")
@login_required
def logout():
    logout_user()
    return jsonify(ok=True)


@bp.get("/auth/me")
def me():
    return jsonify(user=current_user.to_dict() if current_user.is_authenticated else None)
