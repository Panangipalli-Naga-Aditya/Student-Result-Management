from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from .. import db
from ..models import Result
from ..utils import files

bp = Blueprint("results", __name__, url_prefix="/api")
TYPES = {"pdf": ["pdf"], "word": ["doc", "docx"], "excel": ["xls", "xlsx"], "powerpoint": ["ppt", "pptx"], "text": ["txt"], "image": ["jpg", "jpeg", "png", "webp"]}

def query_from_args(a):
    q = Result.query
    s = a.get("q", "").strip()
    if s:
        like = f"%{s}%"
        q = q.filter(db.or_(Result.student_name.ilike(like), Result.roll_number.ilike(like), Result.title.ilike(like), Result.subject.ilike(like)))
    if a.get("subject"): q = q.filter(Result.subject == a["subject"])
    t = a.get("type")
    if t in TYPES: q = q.filter(Result.file_type.in_(TYPES[t]))
    now = datetime.utcnow(); days = {"today": 0, "week": 7, "month": 30}.get(a.get("date"))
    if days is not None:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        q = q.filter(Result.upload_date >= start)
    order = {"oldest": Result.upload_date.asc(), "name": Result.student_name.asc()}.get(a.get("sort"), Result.upload_date.desc())
    return q.order_by(order)

@bp.get("/results")
@bp.get("/results/search")
@bp.get("/results/filter")
@login_required
def list_results(): return jsonify(results=[r.to_dict() for r in query_from_args(request.args).limit(200)])

@bp.get("/results/<int:rid>")
@login_required
def get_result(rid): return jsonify(result=db.get_or_404(Result, rid).to_dict())

@bp.post("/results")
@login_required
def upload():
    f = request.files.get("file")
    title, subject = request.form.get("title", "").strip(), request.form.get("subject", "").strip()
    if not f or not f.filename: return jsonify(error="Please choose a file."), 400
    if not title or not subject: return jsonify(error="Title and subject are required."), 400
    try: ext, cat, mime = files.validate(f)
    except ValueError as e: return jsonify(error=str(e)), 400
    stored, size = files.save(f, current_app.config["UPLOAD_FOLDER"], ext)
    r = Result(student_id=current_user.id, student_name=current_user.name, roll_number=current_user.roll_number,
               title=title[:200], subject=subject[:80], description=request.form.get("description", "")[:2000],
               original_filename=f.filename[:255], stored_filename=stored, file_type=ext, mime_type=mime, file_size=size)
    db.session.add(r); db.session.commit()
    return jsonify(message="Result published successfully!", result=r.to_dict()), 201

@bp.delete("/results/<int:rid>")
@login_required
def delete(rid):
    r = db.get_or_404(Result, rid)
    if r.student_id != current_user.id and not current_user.is_admin:
        return jsonify(error="You do not have permission to perform this action."), 403
    import os
    try: os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], r.stored_filename))
    except OSError: pass
    db.session.delete(r); db.session.commit(); return jsonify(ok=True)

def _send(rid, attach):
    r = db.get_or_404(Result, rid)  # any authenticated user may access shared results
    if not attach and r.file_type not in files.INLINE:
        return jsonify(error="Preview unavailable for this file type."), 415
    resp = send_from_directory(current_app.config["UPLOAD_FOLDER"], r.stored_filename, mimetype=r.mime_type,
                               as_attachment=attach, download_name=r.original_filename)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    if not attach: resp.headers["Content-Security-Policy"] = "sandbox"
    return resp

@bp.get("/results/<int:rid>/download")
@login_required
def download(rid): return _send(rid, True)

@bp.get("/results/<int:rid>/view")
@login_required
def view(rid): return _send(rid, False)

@bp.get("/user/uploads")
@login_required
def my_uploads():
    rs = Result.query.filter_by(student_id=current_user.id).order_by(Result.upload_date.desc()).all()
    return jsonify(results=[r.to_dict() for r in rs])
