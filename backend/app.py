import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import Integer, String, Enum, TIMESTAMP, func, ForeignKey, DECIMAL


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)

    # Config
    app.config['DB_HOST'] = os.getenv('DB_HOST', '127.0.0.1')
    app.config['DB_PORT'] = int(os.getenv('DB_PORT', '3306'))
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'gmc_system')

    # CORS for local dev (adjust origins for prod)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "*"]}})

    # DB URL with SQLite fallback if not provided
    db_url = os.getenv(
        'DB_URL',
        f"mysql+pymysql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}"
        f"@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
    )
    engine = create_engine(db_url, pool_pre_ping=True, future=True)

    # ORM models and auto-migrations (create_all) for SQLite/dev usage
    class Base(DeclarativeBase):
        pass

    class Branch(Base):
        __tablename__ = 'branches'
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(String(100), nullable=False)
        location: Mapped[str] = mapped_column(String(150), nullable=False)
        status: Mapped[str] = mapped_column(Enum('Operational', 'Maintenance', 'Closed', name='branch_status'), default='Operational', nullable=False)
        created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    class InventoryItem(Base):
        __tablename__ = 'inventory_items'
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        branch_id: Mapped[int] = mapped_column(ForeignKey('branches.id'), nullable=False)
        rice_variant: Mapped[str] = mapped_column(String(100), nullable=False)
        stock_kg: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
        price: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0, nullable=False)
        availability: Mapped[str] = mapped_column(Enum('Available', 'Low Stock', 'Out of Stock', name='availability'), default='Available', nullable=False)
        batch_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
        created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
        updated_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # If using SQLite, ensure tables and seed data exist
    if db_url.startswith('sqlite'):  # e.g., sqlite:///gmc.db
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            if session.query(Branch).count() == 0:
                branches = [
                    Branch(name='Marawoy', location='Marawoy, Lipa City', status='Operational'),
                    Branch(name='Bulacnin', location='Bulacnin, Lipa City', status='Operational'),
                    Branch(name='Malvar', location='Malvar, Batangas', status='Maintenance'),
                    Branch(name='Sta. Cruz', location='Sta. Cruz, Laguna', status='Operational'),
                ]
                session.add_all(branches)
                session.flush()
                items = [
                    InventoryItem(branch_id=branches[0].id, rice_variant='Crystal Dinorado', stock_kg=1500, price=45.00, availability='Available', batch_code='RTY1234455'),
                    InventoryItem(branch_id=branches[0].id, rice_variant='Sinandomeng', stock_kg=800, price=42.00, availability='Low Stock', batch_code='RTY1234456'),
                    InventoryItem(branch_id=branches[0].id, rice_variant='Jasmine', stock_kg=0, price=48.00, availability='Out of Stock', batch_code='RTY1234457'),
                ]
                session.add_all(items)
                session.commit()

    @app.get('/api/health')
    def health():
        try:
            with engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            return jsonify({"status": "ok", "database": "connected"})
        except Exception as exc:  # noqa: BLE001 - surfacing error in dev
            return jsonify({"status": "degraded", "database": "error", "detail": str(exc)}), 500

    # --- Frontend serving (Admin_GMC) ---
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ui_root = os.path.join(project_root, 'Admin_GMC')
    page_dir = os.path.join(ui_root, 'page')
    css_dir = os.path.join(ui_root, 'css')
    js_dir = os.path.join(ui_root, 'js')
    img_dir = os.path.join(ui_root, 'image')

    @app.get('/')
    def index():
        # Serve Dashboard by default
        return send_from_directory(page_dir, 'Dashboard.html')

    @app.get('/page/<path:filename>')
    def serve_page(filename: str):
        return send_from_directory(page_dir, filename)

    @app.get('/css/<path:filename>')
    def serve_css(filename: str):
        return send_from_directory(css_dir, filename)

    @app.get('/js/<path:filename>')
    def serve_js(filename: str):
        return send_from_directory(js_dir, filename)

    @app.get('/image/<path:filename>')
    def serve_image(filename: str):
        return send_from_directory(img_dir, filename)

    # Allow direct access like /Inventory.html, /Analytics.html, etc.
    @app.get('/<path:filename>')
    def serve_page_at_root(filename: str):
        if filename.lower().endswith('.html'):
            return send_from_directory(page_dir, filename)
        return jsonify({"error": "Not found"}), 404

    @app.get('/api/ping')
    def ping():
        return jsonify({"message": "pong"})

    @app.get('/api/branches')
    def list_branches():
        try:
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    rows = session.query(Branch).order_by(Branch.id).all()
                    branches = [
                        {
                            "id": r.id,
                            "name": r.name,
                            "location": r.location,
                            "status": r.status,
                            "created_at": None,
                        }
                        for r in rows
                    ]
            else:
                with engine.connect() as conn:
                    result = conn.execute(text(
                        "SELECT id, name, location, status, created_at FROM branches ORDER BY id"
                    ))
                    branches = [
                        {
                            "id": row.id,
                            "name": row.name,
                            "location": row.location,
                            "status": row.status,
                            "created_at": row.created_at.isoformat() if row.created_at else None,
                        }
                        for row in result
                    ]
            return jsonify({"data": branches})
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc)}), 500

    @app.get('/api/branches/<int:branch_id>/inventory')
    def branch_inventory(branch_id: int):
        try:
            page = max(int(request.args.get('page', 1)), 1)
            page_size = min(max(int(request.args.get('page_size', 50)), 1), 200)
            offset = (page - 1) * page_size

            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    q = session.query(InventoryItem).filter(InventoryItem.branch_id == branch_id)
                    total = q.count()
                    rows = q.order_by(InventoryItem.id).offset(offset).limit(page_size).all()
                    items = [
                        {
                            "id": r.id,
                            "branch_id": r.branch_id,
                            "rice_variant": r.rice_variant,
                            "stock_kg": r.stock_kg,
                            "price": float(r.price) if r.price is not None else 0.0,
                            "availability": r.availability,
                            "batch_code": r.batch_code,
                            "created_at": None,
                            "updated_at": None,
                        }
                        for r in rows
                    ]
            else:
                with engine.connect() as conn:
                    items_result = conn.execute(
                        text(
                            """
                            SELECT id, branch_id, rice_variant, stock_kg, price, availability, batch_code, created_at, updated_at
                            FROM inventory_items
                            WHERE branch_id = :branch_id
                            ORDER BY id
                            LIMIT :limit OFFSET :offset
                            """
                        ),
                        {"branch_id": branch_id, "limit": page_size, "offset": offset}
                    )

                    items = [
                        {
                            "id": row.id,
                            "branch_id": row.branch_id,
                            "rice_variant": row.rice_variant,
                            "stock_kg": row.stock_kg,
                            "price": float(row.price) if row.price is not None else 0.0,
                            "availability": row.availability,
                            "batch_code": row.batch_code,
                            "created_at": row.created_at.isoformat() if row.created_at else None,
                            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                        }
                        for row in items_result
                    ]

                    total_result = conn.execute(
                        text("SELECT COUNT(*) AS cnt FROM inventory_items WHERE branch_id = :branch_id"),
                        {"branch_id": branch_id}
                    )
                    total = total_result.scalar_one()

            return jsonify({
                "data": items,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": int(total)
                }
            })
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=True)

