from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import User, Result

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

def admin_required(fn):
    @wraps(fn)
    @login_required
    def w(*a, **k):
        if not current_user.is_admin: return jsonify(error="You do not have permission to perform this action."), 403
        return fn(*a, **k)
    return w

@bp.get("/dashboard")
@admin_required
def dashboard():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return jsonify(
        total_students=User.query.filter_by(role="student").count(),
        total_results=Result.query.count(),
        uploaded_today=Result.query.filter(Result.upload_date >= today).count(),
        storage_bytes=db.session.query(db.func.coalesce(db.func.sum(Result.file_size), 0)).scalar(),
        recent=[r.to_dict() for r in Result.query.order_by(Result.upload_date.desc()).limit(25)])
