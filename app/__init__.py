import os
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf
from config import Config

db = SQLAlchemy(); login = LoginManager(); csrf = CSRFProtect()

def create_app(cfg=Config):
    app = Flask(__name__); app.config.from_object(cfg)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db.init_app(app); login.init_app(app); csrf.init_app(app)
    from . import models
    from .routes import auth, results, admin
    for m in (auth, results, admin): app.register_blueprint(m.bp)

    @login.unauthorized_handler
    def unauth(): return jsonify(error="Please log in to upload a result."), 401
    @app.errorhandler(413)
    def too_big(e): return jsonify(error="File size exceeds the allowed limit."), 413
    @app.errorhandler(400)
    def bad(e): return jsonify(error=getattr(e, "description", "Bad request")), 400
    @app.errorhandler(404)
    def nf(e): return jsonify(error="Not found."), 404
    @app.route("/")
    def index(): return render_template("index.html", csrf=generate_csrf())
    with app.app_context(): db.create_all()
    return app
