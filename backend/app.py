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
    print(f"DEBUG: DATABASE_URL = {database_url}")
    
    if database_url:
        # Production database (Render PostgreSQL)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        print(f"DEBUG: Using production database: {database_url[:50]}...")
    else:
        # Development database (local PostgreSQL)
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:postgres@localhost:5432/gmcdb"
        print("DEBUG: Using development database: PostgreSQL")
    
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
          { "email": "admin@gmc.com", "password": "adminpass" }
          { "email": "manager_marawoy@gmc.com", "password": "managerpass" }
        """
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()
        
        print(f"DEBUG LOGIN: email={email}, password_length={len(password)}")
        
        if not email or not password:
            print("DEBUG LOGIN: Missing email or password")
            return jsonify(ok=False, error="Email and password are required"), 400

        # Try SQLAlchemy ORM first
        user = User.query.filter_by(email=email).first()
        print(f"DEBUG LOGIN: ORM user found: {user is not None}")
        
        # If ORM fails, try raw SQL
        if not user:
            try:
                print("DEBUG LOGIN: Trying raw SQL query")
                raw_user = db.session.execute(db.text("""
                    SELECT id, email, role, branch_id, password_hash 
                    FROM users WHERE email = :email
                """), {"email": email}).fetchone()
                
                print(f"DEBUG LOGIN: Raw SQL result: {raw_user is not None}")
                
                if raw_user:
                    # Create a mock user object for compatibility
                    class MockUser:
                        def __init__(self, row):
                            self.id = row[0]
                            self.email = row[1]
                            self.role = row[2]
                            self.branch_id = row[3]
                            self.password_hash = row[4]
                    
                    user = MockUser(raw_user)
                    print(f"DEBUG LOGIN: MockUser created with hash length: {len(user.password_hash)}")
            except Exception as e:
                print(f"DEBUG LOGIN: Raw SQL query failed: {e}")
                return jsonify(ok=False, error="Database error"), 500
        
        if not user:
            print("DEBUG LOGIN: No user found")
            return jsonify(ok=False, error="Invalid email or password"), 401
            
        print(f"DEBUG LOGIN: User found - email: {user.email}, role: {user.role}")
        print(f"DEBUG LOGIN: Password hash: {user.password_hash[:50]}...")
        
        # Proper password verification using werkzeug
        from werkzeug.security import check_password_hash
        password_valid = check_password_hash(user.password_hash, password)
        print(f"DEBUG LOGIN: Password valid: {password_valid}")
        
        if not password_valid:
            print("DEBUG LOGIN: Password verification failed")
            return jsonify(ok=False, error="Invalid email or password"), 401

        # Create session user
        session_user = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "branch_id": user.branch_id
        }
        
        print(f"DEBUG LOGIN: Login successful for {user.email}")
        session["user"] = session_user
        
        # Log the login activity
        try:
            from activity_logger import ActivityLogger
            ActivityLogger.log_user_login(
                user_id=user.id,
                user_email=user.email,
                branch_id=user.branch_id
            )
        except Exception as e:
            print(f"DEBUG LOGIN: Failed to log activity: {e}")
        
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

    @app.route("/add-inventory")
    def add_inventory():
        """Add inventory data to the database"""
        try:
            from models import InventoryItem, Product, Branch
            
            # Get all products and branches
            products = Product.query.all()
            branches = Branch.query.all()
            
            if not products or not branches:
                return "<h1>Error: No products or branches found. Run seed script first.</h1>"
            
            # Create inventory items for each product in each branch
            created_items = []
            for product in products:
                for branch in branches:
                    # Check if inventory item already exists
                    existing = InventoryItem.query.filter_by(
                        product_id=product.id, 
                        branch_id=branch.id
                    ).first()
                    
                    if not existing:
                        # Generate random stock quantity (100-1000 kg)
                        import random
                        stock_quantity = random.randint(100, 1000)
                        
                        inventory_item = InventoryItem(
                            product_id=product.id,
                            branch_id=branch.id,
                            stock_kg=stock_quantity,
                            unit_price=product.price if hasattr(product, 'price') else 45.0
                        )
                        db.session.add(inventory_item)
                        created_items.append(f"{product.name} in {branch.name}: {stock_quantity}kg")
            
            db.session.commit()
            
            # Create HTML response
            items_html = ""
            for item in created_items:
                items_html += f"<p>✅ {item}</p>"
            
            return f"""
            <h1>Inventory Added Successfully! 🎉</h1>
            <h2>Created Items:</h2>
            {items_html}
            <br>
            <a href="/show-inventory">View All Inventory</a> | 
            <a href="/login">Go to Login</a>
            """
            
        except Exception as e:
            return f"<h1>Error adding inventory:</h1><p>{str(e)}</p>"

    @app.route("/add-users")
    def add_users():
        """Add users without deleting existing data"""
        try:
            from models import User, Branch
            from werkzeug.security import generate_password_hash
            
            # Create branches if they don't exist
            branches_data = ["Marawoy", "Lipa", "Malvar", "Bulacnin", "Boac", "Sta. Cruz"]
            for branch_name in branches_data:
                existing_branch = Branch.query.filter_by(name=branch_name).first()
                if not existing_branch:
                    branch = Branch(name=branch_name, status="operational")
                    db.session.add(branch)
            
            db.session.commit()
            
            # Get all branches
            branches = Branch.query.all()
            
            # Create admin user if doesn't exist
            admin = User.query.filter_by(email="admin@gmc.com").first()
            if not admin:
                admin = User(
                    email="admin@gmc.com",
                    password_hash=generate_password_hash("adminpass"),
                    role="admin",
                    branch_id=None
                )
                db.session.add(admin)
            
            # Create manager users if they don't exist
            managers_created = []
            for branch in branches:
                email = f"manager_{branch.name.lower().replace(' ', '').replace('.', '')}@gmc.com"
                existing_manager = User.query.filter_by(email=email).first()
                if not existing_manager:
                    manager = User(
                        email=email,
                        password_hash=generate_password_hash("managerpass"),
                        role="manager",
                        branch_id=branch.id
                    )
                    db.session.add(manager)
                    managers_created.append(f"{branch.name}: {email}")
            
            db.session.commit()
            
            # Create HTML response
            managers_html = ""
            for manager in managers_created:
                managers_html += f"<p><strong>{manager}</strong><br>Password: managerpass</p>"
            
            return f"""
            <h1>Users Added Successfully! 🎉</h1>
            <h2>Login Credentials:</h2>
            
            <h3>👨‍💼 ADMIN:</h3>
            <p><strong>Email:</strong> admin@gmc.com<br><strong>Password:</strong> adminpass</p>
            
            <h3>👨‍💼 MANAGERS:</h3>
            {managers_html}
            
            <br>
            <a href="/login">Go to Login Page</a>
            """
            
        except Exception as e:
            return f"<h1>Error adding users:</h1><p>{str(e)}</p><a href='/login'>Go to Login Page</a>"

    @app.route("/show-inventory")
    def show_inventory():
        """Show all inventory items in the database"""
        try:
            from models import InventoryItem, Product, Branch
            
            items = InventoryItem.query.all()
            html = "<h1>Inventory Items in Database:</h1>"
            
            for item in items:
                product = Product.query.get(item.product_id)
                branch = Branch.query.get(item.branch_id)
                html += f"<p><strong>Product:</strong> {product.name if product else 'Unknown'} | <strong>Branch:</strong> {branch.name if branch else 'Unknown'} | <strong>Stock:</strong> {item.stock_kg}kg</p>"
            
            return html
            
        except Exception as e:
            return f"<h1>Error:</h1><p>{str(e)}</p>"

    @app.route("/show-users")
    def show_users():
        """Show all users in the database"""
        try:
            from models import User
            
            users = User.query.all()
            html = "<h1>Users in Database:</h1>"
            
            for user in users:
                html += f"<p><strong>{user.role.upper()}:</strong> {user.email} (Password hash: {user.password_hash[:20]}...)</p>"
            
            return html
            
        except Exception as e:
            return f"<h1>Error:</h1><p>{str(e)}</p>"

    @app.route("/fix-passwords")
    def fix_passwords():
        """Fix password hashing for existing users"""
        try:
            from models import User
            from werkzeug.security import generate_password_hash
            
            # Update admin password
            admin = User.query.filter_by(email='admin@gmc.com').first()
            if admin:
                admin.password_hash = generate_password_hash('adminpass')
                print('Updated admin password')
            
            # Update manager passwords
            managers = User.query.filter_by(role='manager').all()
            for manager in managers:
                manager.password_hash = generate_password_hash('managerpass')
                print(f'Updated manager password: {manager.email}')
            
            db.session.commit()
            
            return """
            <h1>Passwords Fixed Successfully! 🎉</h1>
            <h2>Login Credentials:</h2>
            <h3>👨‍💼 ADMIN:</h3>
            <p><strong>Email:</strong> admin@gmc.com<br><strong>Password:</strong> adminpass</p>
            <h3>👨‍💼 MANAGERS:</h3>
            <p>Use any manager email with password: <strong>managerpass</strong></p>
            <br>
            <a href="/login">Go to Login Page</a>
            """
            
        except Exception as e:
            return f"<h1>Error fixing passwords:</h1><p>{str(e)}</p><a href='/login'>Go to Login Page</a>"

    @app.route("/seed-database")
    def seed_database():
        """Seed the database with default users and sample data"""
        try:
            from models import User, Branch
            from werkzeug.security import generate_password_hash
            
            # Create branches first
            branches_data = [
                "Marawoy", "Lipa", "Malvar", "Bulacnin", "Boac", "Sta. Cruz"
            ]
            
            for branch_name in branches_data:
                existing_branch = Branch.query.filter_by(name=branch_name).first()
                if not existing_branch:
                    branch = Branch(name=branch_name, status="operational")
                    db.session.add(branch)
            
            db.session.commit()
            
            # Get all branches for manager creation
            branches = Branch.query.all()
            
            # Create admin user
            admin_user = User.query.filter_by(email="admin@gmc.com").first()
            if not admin_user:
                admin_user = User(
                    email="admin@gmc.com",
                    password_hash=generate_password_hash("adminpass"),
                    role="admin",
                    branch_id=None
                )
                db.session.add(admin_user)
            
            # Create manager users for each branch
            created_managers = []
            for branch in branches:
                email = f"manager_{branch.name.lower().replace(' ', '').replace('.', '')}@gmc.com"
                existing_manager = User.query.filter_by(email=email).first()
                if not existing_manager:
                    manager = User(
                        email=email,
                        password_hash=generate_password_hash("managerpass"),
                        role="manager",
                        branch_id=branch.id
                    )
                    db.session.add(manager)
                    created_managers.append(f"{branch.name}: {email}")
            
            db.session.commit()
            
            # Create HTML response
            managers_html = ""
            for manager in created_managers:
                managers_html += f"<p><strong>{manager}</strong><br>Password: managerpass</p>"
            
            return f"""
            <h1>Database Seeded Successfully! 🎉</h1>
            <h2>Default Login Credentials:</h2>
            
            <h3>👨‍💼 ADMIN ACCESS:</h3>
            <p><strong>Email:</strong> admin@gmc.com<br><strong>Password:</strong> adminpass</p>
            
            <h3>👨‍💼 MANAGER ACCESS:</h3>
            <p>Choose any branch manager:</p>
            {managers_html}
            
            <br>
            <a href="/login">Go to Login Page</a>
            """
            
        except Exception as e:
            return f"<h1>Error seeding database:</h1><p>{str(e)}</p><a href='/login'>Go to Login Page</a>"

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

    # --- Debug endpoints for password troubleshooting ---
    @app.get("/debug-passwords")
    def debug_passwords():
        """Debug endpoint to show all users and their password hashes"""
        try:
            # Try SQLAlchemy ORM first
            users = User.query.all()
            result = []
            for user in users:
                result.append({
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "branch_id": user.branch_id,
                    "password_hash": user.password_hash,
                    "password_length": len(user.password_hash) if user.password_hash else 0
                })
            
            # If no users found with ORM, try raw SQL
            if len(result) == 0:
                raw_users = db.session.execute(db.text("SELECT id, email, role, branch_id, password_hash FROM users")).fetchall()
                for row in raw_users:
                    result.append({
                        "id": row[0],
                        "email": row[1],
                        "role": row[2],
                        "branch_id": row[3],
                        "password_hash": row[4],
                        "password_length": len(row[4]) if row[4] else 0
                    })
            
            return jsonify({
                "total_users": len(result),
                "users": result,
                "database_url": app.config["SQLALCHEMY_DATABASE_URI"][:50] + "..." if len(app.config["SQLALCHEMY_DATABASE_URI"]) > 50 else app.config["SQLALCHEMY_DATABASE_URI"],
                "query_method": "ORM" if len(User.query.all()) > 0 else "Raw SQL"
            })
        except Exception as e:
            return jsonify({"error": str(e), "type": type(e).__name__})
    
    @app.get("/debug-login")
    def debug_login():
        """Debug endpoint to test login with any password"""
        email = request.args.get('email', 'admin@gmc.com')
        password = request.args.get('password', 'adminpass')
        
        try:
            # Try ORM first
            user = User.query.filter_by(email=email).first()
            method = "ORM"
            
            # If ORM fails, try raw SQL
            if not user:
                try:
                    raw_user = db.session.execute(db.text("""
                        SELECT id, email, role, branch_id, password_hash 
                        FROM users WHERE email = :email
                    """), {"email": email}).fetchone()
                    
                    if raw_user:
                        class MockUser:
                            def __init__(self, row):
                                self.id = row[0]
                                self.email = row[1]
                                self.role = row[2]
                                self.branch_id = row[3]
                                self.password_hash = row[4]
                        
                        user = MockUser(raw_user)
                        method = "Raw SQL"
                except Exception as sql_error:
                    return jsonify({"error": f"Both ORM and Raw SQL failed: {sql_error}", "type": type(sql_error).__name__})
            
            if not user:
                return jsonify({"error": "User not found", "email": email, "method": method})
            
            from werkzeug.security import check_password_hash
            is_valid = check_password_hash(user.password_hash, password)
            
            return jsonify({
                "email": email,
                "password": password,
                "user_found": True,
                "password_valid": is_valid,
                "stored_hash": user.password_hash,
                "hash_length": len(user.password_hash) if user.password_hash else 0,
                "hash_type": user.password_hash.split(':')[0] if user.password_hash and ':' in user.password_hash else "unknown",
                "method": method
            })
        except Exception as e:
            return jsonify({"error": str(e), "type": type(e).__name__})
    
    @app.get("/debug-database")
    def debug_database():
        """Debug endpoint to check database connection and basic queries"""
        try:
            # Test basic connection
            db.session.execute(db.text("SELECT 1"))
            
            # Check table counts
            branches_count = db.session.execute(db.text("SELECT COUNT(*) FROM branches")).scalar()
            users_count = db.session.execute(db.text("SELECT COUNT(*) FROM users")).scalar()
            products_count = db.session.execute(db.text("SELECT COUNT(*) FROM products")).scalar()
            
            return jsonify({
                "database_connected": True,
                "branches_count": branches_count,
                "users_count": users_count,
                "products_count": products_count,
                "database_url": app.config["SQLALCHEMY_DATABASE_URI"][:50] + "..." if len(app.config["SQLALCHEMY_DATABASE_URI"]) > 50 else app.config["SQLALCHEMY_DATABASE_URI"]
            })
        except Exception as e:
            return jsonify({
                "database_connected": False,
                "error": str(e),
                "type": type(e).__name__,
                "database_url": app.config["SQLALCHEMY_DATABASE_URI"][:50] + "..." if len(app.config["SQLALCHEMY_DATABASE_URI"]) > 50 else app.config["SQLALCHEMY_DATABASE_URI"]
            })
    
    @app.get("/debug-users-detail")
    def debug_users_detail():
        """Debug endpoint to show detailed user information"""
        try:
            users = User.query.all()
            result = []
            for user in users:
                result.append({
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "branch_id": user.branch_id,
                    "password_hash": user.password_hash,
                    "password_length": len(user.password_hash) if user.password_hash else 0,
                    "hash_type": user.password_hash.split(':')[0] if user.password_hash and ':' in user.password_hash else "unknown",
                    "created_at": str(user.created_at) if hasattr(user, 'created_at') else "N/A"
                })
            return jsonify({
                "total_users": len(result),
                "users": result
            })
        except Exception as e:
            return jsonify({"error": str(e), "type": type(e).__name__})
    
    @app.get("/fix-password-hashes")
    def fix_password_hashes():
        """Fix malformed password hashes in the database"""
        try:
            from werkzeug.security import generate_password_hash
            
            # Generate proper hashes
            admin_hash = generate_password_hash("adminpass")
            manager_hash = generate_password_hash("managerpass")
            
            # Update admin user
            admin_updated = db.session.execute(db.text("""
                UPDATE users SET password_hash = :hash WHERE email = 'admin@gmc.com'
            """), {"hash": admin_hash})
            
            # Update manager users
            managers_updated = db.session.execute(db.text("""
                UPDATE users SET password_hash = :hash WHERE role = 'manager'
            """), {"hash": manager_hash})
            
            db.session.commit()
            
            # Verify the fix
            users = db.session.execute(db.text("""
                SELECT email, role, password_hash FROM users ORDER BY role, email
            """)).fetchall()
            
            users_html = ""
            for user in users:
                users_html += f"<p><strong>{user[1].upper()}:</strong> {user[0]}<br>Hash: {user[2][:50]}...</p>"
            
            return f"""
            <h1>Password Hashes Fixed Successfully! 🎉</h1>
            <h2>Updated Users:</h2>
            {users_html}
            
            <h2>Login Credentials:</h2>
            <h3>👨‍💼 ADMIN:</h3>
            <p><strong>Email:</strong> admin@gmc.com<br><strong>Password:</strong> adminpass</p>
            
            <h3>👨‍💼 MANAGERS:</h3>
            <p>Use any manager email with password: <strong>managerpass</strong></p>
            
            <br>
            <a href="/debug-login?email=admin@gmc.com&password=adminpass">Test Admin Login</a> | 
            <a href="/login">Go to Login Page</a>
            """
            
        except Exception as e:
            return f"<h1>Error fixing password hashes:</h1><p>{str(e)}</p><a href='/debug-database'>Check Database</a>"

    @app.get("/seed-render-database")
    def seed_render_database():
        """Seed the Render database with users and data"""
        try:
            from werkzeug.security import generate_password_hash
            
            # Check if users already exist using raw SQL
            existing_users = db.session.execute(db.text("SELECT COUNT(*) FROM users")).scalar()
            
            if existing_users > 0:
                return f"""
                <h1>Database Already Has Users! 🎉</h1>
                <p>Found {existing_users} users in the database.</p>
                <p><a href="/debug-passwords">Check Users</a> | <a href="/login">Go to Login</a></p>
                """
            
            # Create branches if they don't exist using raw SQL
            branches_data = [
                {"name": "Marawoy", "location": "Marawoy, Lipa City"},
                {"name": "Lipa", "location": "Lipa, Batangas"},
                {"name": "Malvar", "location": "Malvar, Batangas"},
                {"name": "Bulacnin", "location": "Bulacnin, Lipa City"},
                {"name": "Boac", "location": "Boac, Marinduque"},
                {"name": "Sta. Cruz", "location": "Sta. Cruz, Laguna"}
            ]
            
            created_branches = []
            for branch_data in branches_data:
                # Check if branch exists using raw SQL
                existing = db.session.execute(db.text("SELECT COUNT(*) FROM branches WHERE name = :name"), 
                                            {"name": branch_data["name"]}).scalar()
                if existing == 0:
                    db.session.execute(db.text("""
                        INSERT INTO branches (name, location, status) 
                        VALUES (:name, :location, 'operational')
                    """), {
                        "name": branch_data["name"],
                        "location": branch_data["location"]
                    })
                    created_branches.append(branch_data["name"])
            
            db.session.commit()
            
            # Get all branches using raw SQL
            branches = db.session.execute(db.text("SELECT id, name FROM branches")).fetchall()
            
            # Create admin user using raw SQL
            admin_exists = db.session.execute(db.text("SELECT COUNT(*) FROM users WHERE email = 'admin@gmc.com'")).scalar()
            if admin_exists == 0:
                admin_hash = generate_password_hash("adminpass")
                db.session.execute(db.text("""
                    INSERT INTO users (email, password_hash, role, branch_id) 
                    VALUES ('admin@gmc.com', :hash, 'admin', NULL)
                """), {"hash": admin_hash})
            
            # Create manager users using raw SQL
            created_managers = []
            for branch in branches:
                email = f"manager_{branch[1].lower().replace(' ', '').replace('.', '')}@gmc.com"
                manager_exists = db.session.execute(db.text("SELECT COUNT(*) FROM users WHERE email = :email"), 
                                                  {"email": email}).scalar()
                if manager_exists == 0:
                    manager_hash = generate_password_hash("managerpass")
                    db.session.execute(db.text("""
                        INSERT INTO users (email, password_hash, role, branch_id) 
                        VALUES (:email, :hash, 'manager', :branch_id)
                    """), {
                        "email": email,
                        "hash": manager_hash,
                        "branch_id": branch[0]
                    })
                    created_managers.append(f"{branch[1]}: {email}")
            
            db.session.commit()
            
            return f"""
            <h1>Render Database Seeded Successfully! 🎉</h1>
            <h2>Created Branches:</h2>
            <p>{', '.join(created_branches) if created_branches else 'All branches already existed'}</p>
            
            <h2>Login Credentials:</h2>
            <h3>👨‍💼 ADMIN:</h3>
            <p><strong>Email:</strong> admin@gmc.com<br><strong>Password:</strong> adminpass</p>
            
            <h3>👨‍💼 MANAGERS:</h3>
            <p>Use any of these:</p>
            <ul>
                <li>manager_marawoy@gmc.com - Password: managerpass</li>
                <li>manager_lipa@gmc.com - Password: managerpass</li>
                <li>manager_malvar@gmc.com - Password: managerpass</li>
                <li>manager_bulacnin@gmc.com - Password: managerpass</li>
                <li>manager_boac@gmc.com - Password: managerpass</li>
                <li>manager_stacruz@gmc.com - Password: managerpass</li>
            </ul>
            
            <br>
            <a href="/debug-passwords">Check Users</a> | 
            <a href="/login">Go to Login</a>
            """
            
        except Exception as e:
            return f"<h1>Error seeding database:</h1><p>{str(e)}</p><a href='/debug-database'>Check Database</a>"

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
