from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from .. import db
from ..models import User, Result, SiteNotice

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_required(fn):
    @wraps(fn)
    @login_required
    def w(*a, **k):
        if not current_user.is_admin:
            return jsonify(error="You do not have permission to perform this action."), 403
        return fn(*a, **k)
    return w


@bp.get("/notice")
def get_notice():
    """Public home-page notice. It is stored in the database, not browser/session storage."""
    notice = SiteNotice.query.order_by(SiteNotice.id.asc()).first()
    return jsonify(notice=notice.to_dict() if notice else None)


@bp.put("/notice")
@admin_required
def update_notice():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if len(message) > 5000:
        return jsonify(error="Notice is too long. Please keep it under 5000 characters."), 400

    notice = SiteNotice.query.order_by(SiteNotice.id.asc()).first()
    if notice is None:
        notice = SiteNotice(message=message, updated_by=current_user.id)
        db.session.add(notice)
    else:
        notice.message = message
        notice.updated_by = current_user.id

    db.session.commit()
    return jsonify(notice=notice.to_dict())


@bp.get("/dashboard")
@admin_required
def dashboard():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    notice = SiteNotice.query.order_by(SiteNotice.id.asc()).first()
    return jsonify(
        total_students=User.query.filter_by(role="student").count(),
        total_results=Result.query.count(),
        uploaded_today=Result.query.filter(Result.upload_date >= today).count(),
        storage_bytes=db.session.query(db.func.coalesce(db.func.sum(Result.file_size), 0)).scalar(),
        notice=notice.to_dict() if notice else None,
        recent=[r.to_dict() for r in Result.query.order_by(Result.upload_date.desc()).limit(25)],
    )
