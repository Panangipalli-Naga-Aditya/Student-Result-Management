from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.relationship("Result", backref="student", cascade="all, delete-orphan")
    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)
    @property
    def is_admin(self): return self.role == "admin"
    def to_dict(self): return dict(id=self.id, name=self.name, roll_number=self.roll_number, email=self.email, role=self.role)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    student_name = db.Column(db.String(120), nullable=False, index=True)
    roll_number = db.Column(db.String(40), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text, default="")
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(80), nullable=False, unique=True)
    file_type = db.Column(db.String(10), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    def to_dict(self):  # never exposes stored_filename / paths
        return dict(id=self.id, student_id=self.student_id, student_name=self.student_name, roll_number=self.roll_number,
                    title=self.title, subject=self.subject, description=self.description, original_filename=self.original_filename,
                    file_type=self.file_type, file_size=self.file_size, upload_date=self.upload_date.isoformat() + "Z")

@login.user_loader
def load_user(uid): return db.session.get(User, int(uid))
