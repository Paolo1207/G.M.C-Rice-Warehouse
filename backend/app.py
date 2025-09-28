# app.py
import os
from flask import Flask, redirect, url_for, jsonify, session, request, render_template_string, render_template
from flask_migrate import Migrate
from flask_caching import Cache
from dotenv import load_dotenv

from Admin_GMC import admin_bp
from GMCmanager import manager_bp
from extensions import db
from models import Branch, Product, InventoryItem, RestockLog, User, ForecastData, SalesTransaction


def create_app() -> Flask:
    # Load .env first
    load_dotenv()

    app = Flask(__name__)

    # === Core config ===
    # Database configuration - use DATABASE_URL from environment (Render) or fallback to local
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Production database (Render PostgreSQL)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Development database (local PostgreSQL)
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:postgres@localhost:5432/gmcdb"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    # IMPORTANT: session secret (use a strong value in .env)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    
    # Cache config
    app.config["CACHE_TYPE"] = "simple"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # 5 minutes

    # Init ORM, migrations, and cache
    db.init_app(app)
    Migrate(app, db)
    cache = Cache(app)

    # Blueprints
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(manager_bp, url_prefix="/manager")

    # ---------- Small helpers ----------
    @app.before_request
    def _attach_user():
        # Make session user accessible if you want (optional)
        request.current_user = session.get("user")

    # ---------- Dummy auth endpoints ----------
    @app.post("/login")
    def login():
        """
        Body (JSON):
          { "email": "admin@gmc.com", "password": "admin123" }
          { "email": "marawoy.manager@gmc.com", "password": "manager123" }
        """
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()
        
        if not email or not password:
            return jsonify(ok=False, error="Email and password are required"), 400

        # Find user in database
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify(ok=False, error="Invalid email or password"), 401
            
        # Simple password check (in production, use proper hashing)
        if user.password_hash != password:
            return jsonify(ok=False, error="Invalid email or password"), 401

        # Create session user
        session_user = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "branch_id": user.branch_id
        }
        
        session["user"] = session_user
        return jsonify(ok=True, user=session_user)

    @app.post("/logout")
    def logout():
        session.pop("user", None)
        return jsonify(ok=True, message="Logged out")

    @app.get("/whoami")
    def whoami():
        return jsonify(ok=True, user=session.get("user"))

    # ---------- Login Pages ----------
    @app.get("/login")
    def login_page():
        return render_template("login.html")
    
    @app.get("/admin-login")
    def admin_login_page():
        return render_template("admin-login.html")
    
    @app.get("/manager-login")
    def manager_login_page():
        return render_template("manager-login.html")

    # ---------- Quick Auth Demo Page ----------
    @app.get("/_auth")
    def auth_demo():
        return render_template_string("""
<!doctype html>
<meta charset="utf-8">
<title>Auth Demo</title>
<style>
  :root{color-scheme:light dark}
  body{font-family:system-ui,Segoe UI,Roboto,Inter,Arial;margin:40px;max-width:900px}
  h1{margin:0 0 16px;display:flex;gap:10px;align-items:center}
  h1::before{content:"🔐";font-size:1.2em}
  .card{border:1px solid #ddd;border-radius:12px;padding:16px;margin:12px 0}
  label{display:block;margin:8px 0 4px}
  input,select,button{padding:10px;border:1px solid #ccc;border-radius:8px}
  button{cursor:pointer}
  .row{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  pre{background:#fafafa;border:1px solid #eee;border-radius:8px;padding:12px;overflow:auto}
  a{margin-right:12px}
</style>

<h1>Quick Auth Demo</h1>

<div class="card">
  <div class="row">
    <div>
      <label>Role</label>
      <select id="role">
        <option value="admin">admin</option>
        <option value="manager">manager</option>
      </select>
    </div>
    <div>
      <label>Branch ID (for manager)</label>
      <input id="branch" type="number" value="1" min="1">
    </div>
  </div>
  <div class="row" style="margin-top:12px">
    <button id="btnLogin">Login</button>
    <button id="btnLogout">Logout</button>
    <button id="btnWho">Who am I?</button>
  </div>
</div>

<div class="card">
  <div class="row">
    <a href="/admin/dashboard" target="_blank">/admin/dashboard</a>
    <a href="/admin/inventory" target="_blank">/admin/inventory</a>
    <span style="width:16px"></span>
    <a href="/manager/dashboard" target="_blank">/manager/dashboard</a>
    <a href="/manager/inventory" target="_blank">/manager/inventory</a>
  </div>
</div>

<div class="card">
  <strong>Response</strong>
  <pre id="out">{}</pre>
</div>

<script>
const out = document.getElementById('out');
const show = (obj) => out.textContent = JSON.stringify(obj, null, 2);

document.getElementById('btnLogin').onclick = async () => {
  const role = document.getElementById('role').value;
  const branch = Number(document.getElementById('branch').value || 1);
  const body = role === 'manager' ? { role, branch_id: branch } : { role };
  const res = await fetch('/login', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  show(await res.json());
};

document.getElementById('btnLogout').onclick = async () => {
  const res = await fetch('/logout', { method:'POST' });
  show(await res.json());
};

document.getElementById('btnWho').onclick = async () => {
  const res = await fetch('/whoami');
  show(await res.json());
};
</script>
        """)

    # ---------- Existing routes ----------
    @app.route("/")
    def root():
        return redirect(url_for("login_page"))

    @app.route("/admin")
    def admin_root():
        return redirect(url_for("admin.admin_dashboard"))

    @app.route("/manager")
    def manager_root():
        return redirect(url_for("manager.manager_dashboard"))

    @app.get("/api/ping")
    def ping():
        return jsonify({"message": "pong"})

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Not found"}), 404

    # ---------- First-run setup + seeding ----------
    with app.app_context():
        db.create_all()
        db.session.execute(db.text("SELECT 1"))

        # --- Seed branches if missing ---
        branches = [
            "Marawoy", "Lipa", "Malvar", "Bulacnin", "Boac", "Sta. Cruz"
        ]
        for name in branches:
            exists = Branch.query.filter_by(name=name).first()
            if not exists:
                db.session.add(Branch(name=name, status="operational"))
        db.session.commit()

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
