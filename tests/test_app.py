import io, os, tempfile, unittest
from config import Config
from app import create_app, db
from app.models import User

class T(Config):
    TESTING = True; WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"; UPLOAD_FOLDER = tempfile.mkdtemp(); MAX_CONTENT_LENGTH = 1024 * 1024

def reg(c, n, roll):
    return c.post("/api/auth/register", json=dict(name=n, roll_number=roll, email=f"{roll}@x.com", password="password1", confirm_password="password1"))
def up(c, name, data, mime, title="T"):
    return c.post("/api/results", data=dict(title=title, subject="Engineering Physics", file=(io.BytesIO(data), name, mime)), content_type="multipart/form-data")

class Suite(unittest.TestCase):
    def setUp(self):
        self.app = create_app(T); self.a = self.app.test_client(); self.b = self.app.test_client()
    def test_flow(self):
        self.assertEqual(reg(self.a, "Alice", "R1").status_code, 201); reg(self.b, "Bob", "R2")
        self.assertEqual(self.a.post("/api/auth/login", json=dict(identifier="R1", password="bad")).status_code, 401)
        self.assertEqual(up(self.a, "a.pdf", b"%PDF-1.4 x", "application/pdf").status_code, 201)
        self.assertEqual(up(self.a, "a.txt", b"hello", "text/plain").status_code, 201)
        self.assertEqual(up(self.a, "a.png", b"\x89PNG\r\n\x1a\n", "image/png").status_code, 201)
        self.assertEqual(up(self.a, "a.docx", b"PK\x03\x04", "application/vnd.openxmlformats-officedocument.wordprocessingml.document").status_code, 201)
        self.assertEqual(up(self.a, "evil.exe", b"MZ", "application/octet-stream").status_code, 400)
        self.assertEqual(up(self.a, "big.pdf", b"%PDF" + b"0" * 2_000_000, "application/pdf").status_code, 413)
        rs = self.b.get("/api/results").get_json()["results"]; self.assertEqual(len(rs), 4)
        self.assertEqual(self.b.get("/api/results?q=R1").get_json()["results"].__len__(), 4)
        self.assertEqual(len(self.b.get("/api/results?type=pdf").get_json()["results"]), 1)
        pid = [r for r in rs if r["file_type"] == "pdf"][0]["id"]
        self.assertEqual(self.b.get(f"/api/results/{pid}/view").status_code, 200)
        self.assertEqual(self.b.get(f"/api/results/{pid}/download").data[:4], b"%PDF")
        self.assertEqual(self.b.delete(f"/api/results/{pid}").status_code, 403)
        with self.app.app_context():
            u = User.query.filter_by(roll_number="R2").first(); u.role = "admin"; db.session.commit()
        self.assertEqual(self.b.get("/api/admin/dashboard").status_code, 200)
        self.assertEqual(self.b.delete(f"/api/results/{pid}").status_code, 200)
        self.assertEqual(self.a.delete(f"/api/results/{rs[0]['id']}").status_code, 200)
        self.assertEqual(self.a.post("/api/auth/logout").status_code, 200)
        self.assertEqual(self.a.get("/api/results").status_code, 401)
if __name__ == "__main__": unittest.main()
