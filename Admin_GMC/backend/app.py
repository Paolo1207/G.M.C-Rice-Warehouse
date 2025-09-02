import os
from flask import Flask, jsonify, request, render_template, send_from_directory

from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import Integer, String, Enum, TIMESTAMP, func, ForeignKey, DECIMAL, Date, Text
from datetime import datetime, timedelta
import random


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

    class User(Base):
        __tablename__ = 'users'
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(String(100), nullable=False)
        warehouse_id: Mapped[str] = mapped_column(String(50), nullable=False)
        location: Mapped[str] = mapped_column(String(150), nullable=False)
        contact_number: Mapped[str] = mapped_column(String(20), nullable=False)
        role: Mapped[str] = mapped_column(Enum('Admin', 'Manager', 'Staff', name='user_role'), default='Staff', nullable=False)
        email: Mapped[str] = mapped_column(String(100), nullable=True)
        created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    class Sales(Base):
        __tablename__ = 'sales'
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        branch_id: Mapped[int] = mapped_column(ForeignKey('branches.id'), nullable=False)
        rice_variant: Mapped[str] = mapped_column(String(100), nullable=False)
        quantity_kg: Mapped[int] = mapped_column(Integer, nullable=False)
        price_per_kg: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
        total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
        customer_name: Mapped[str] = mapped_column(String(100), nullable=True)
        sale_date: Mapped[str] = mapped_column(Date, nullable=False)
        created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    class Purchase(Base):
        __tablename__ = 'purchases'
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        branch_id: Mapped[int] = mapped_column(ForeignKey('branches.id'), nullable=False)
        rice_variant: Mapped[str] = mapped_column(String(100), nullable=False)
        quantity_kg: Mapped[int] = mapped_column(Integer, nullable=False)
        price_per_kg: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
        total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
        supplier_name: Mapped[str] = mapped_column(String(100), nullable=True)
        purchase_date: Mapped[str] = mapped_column(Date, nullable=False)
        status: Mapped[str] = mapped_column(Enum('Pending', 'Delivered', 'Cancelled', name='purchase_status'), default='Pending', nullable=False)
        created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    class Delivery(Base):
        __tablename__ = 'deliveries'
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        branch_id: Mapped[int] = mapped_column(ForeignKey('branches.id'), nullable=False)
        customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
        rice_variant: Mapped[str] = mapped_column(String(100), nullable=False)
        quantity_kg: Mapped[int] = mapped_column(Integer, nullable=False)
        delivery_date: Mapped[str] = mapped_column(Date, nullable=False)
        status: Mapped[str] = mapped_column(Enum('Scheduled', 'In Transit', 'Delivered', 'Cancelled', name='delivery_status'), default='Scheduled', nullable=False)
        address: Mapped[str] = mapped_column(Text, nullable=True)
        contact_number: Mapped[str] = mapped_column(String(20), nullable=True)
        created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    class Notification(Base):
        __tablename__ = 'notifications'
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        title: Mapped[str] = mapped_column(String(200), nullable=False)
        message: Mapped[str] = mapped_column(Text, nullable=False)
        type: Mapped[str] = mapped_column(Enum('Info', 'Warning', 'Error', 'Success', name='notification_type'), default='Info', nullable=False)
        is_read: Mapped[bool] = mapped_column(Integer, default=0, nullable=False)  # SQLite boolean
        created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    # If using SQLite, ensure tables and seed data exist
    if db_url.startswith('sqlite'):  # e.g., sqlite:///gmc.db
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            # Seed branches
            if session.query(Branch).count() == 0:
                branches = [
                    Branch(name='Marawoy', location='Marawoy, Lipa City', status='Operational'),
                    Branch(name='Bulacnin', location='Bulacnin, Lipa City', status='Operational'),
                    Branch(name='Malvar', location='Malvar, Batangas', status='Maintenance'),
                    Branch(name='Sta. Cruz', location='Sta. Cruz, Laguna', status='Operational'),
                ]
                session.add_all(branches)
                session.flush()
                
                # Seed inventory
                items = [
                    InventoryItem(branch_id=branches[0].id, rice_variant='Crystal Dinorado', stock_kg=1500, price=45.00, availability='Available', batch_code='RTY1234455'),
                    InventoryItem(branch_id=branches[0].id, rice_variant='Sinandomeng', stock_kg=800, price=42.00, availability='Low Stock', batch_code='RTY1234456'),
                    InventoryItem(branch_id=branches[0].id, rice_variant='Jasmine', stock_kg=0, price=48.00, availability='Out of Stock', batch_code='RTY1234457'),
                    InventoryItem(branch_id=branches[1].id, rice_variant='Crystal Dinorado', stock_kg=2000, price=45.00, availability='Available', batch_code='RTY1234458'),
                    InventoryItem(branch_id=branches[1].id, rice_variant='Sinandomeng', stock_kg=1200, price=42.00, availability='Available', batch_code='RTY1234459'),
                ]
                session.add_all(items)
                
                # Seed users
                users = [
                    User(name='John Smith', warehouse_id='WH001', location='Marawoy, Lipa City', contact_number='09123456789', role='Manager', email='john@gmc.com'),
                    User(name='Maria Garcia', warehouse_id='WH002', location='Bulacnin, Lipa City', contact_number='09234567890', role='Staff', email='maria@gmc.com'),
                    User(name='Carlos Santos', warehouse_id='WH003', location='Malvar, Batangas', contact_number='09345678901', role='Admin', email='carlos@gmc.com'),
                ]
                session.add_all(users)
                
                # Seed sales data (last 30 days)
                rice_variants = ['Crystal Dinorado', 'Sinandomeng', 'Jasmine', 'Premium Rice']
                for i in range(30):
                    sale_date = datetime.now() - timedelta(days=i)
                    for branch in branches:
                        for variant in rice_variants:
                            quantity = random.randint(50, 300)
                            price = random.uniform(40, 50)
                            sales = Sales(
                                branch_id=branch.id,
                                rice_variant=variant,
                                quantity_kg=quantity,
                                price_per_kg=price,
                                total_amount=quantity * price,
                                customer_name=f'Customer {random.randint(1, 20)}',
                                sale_date=sale_date.date()
                            )
                            session.add(sales)
                
                # Seed purchases
                suppliers = ['ABC Rice Supplier', 'XYZ Trading', 'Premium Rice Co.', 'Local Farmers Coop']
                for i in range(20):
                    purchase_date = datetime.now() - timedelta(days=random.randint(1, 60))
                    purchase = Purchase(
                        branch_id=random.choice(branches).id,
                        rice_variant=random.choice(rice_variants),
                        quantity_kg=random.randint(500, 2000),
                        price_per_kg=random.uniform(35, 45),
                        total_amount=0,  # Will be calculated
                        supplier_name=random.choice(suppliers),
                        purchase_date=purchase_date.date(),
                        status=random.choice(['Pending', 'Delivered', 'Delivered'])
                    )
                    purchase.total_amount = purchase.quantity_kg * purchase.price_per_kg
                    session.add(purchase)
                
                # Seed deliveries
                for i in range(15):
                    delivery_date = datetime.now() + timedelta(days=random.randint(1, 30))
                    delivery = Delivery(
                        branch_id=random.choice(branches).id,
                        customer_name=f'Customer {random.randint(1, 50)}',
                        rice_variant=random.choice(rice_variants),
                        quantity_kg=random.randint(25, 200),
                        delivery_date=delivery_date.date(),
                        status=random.choice(['Scheduled', 'In Transit', 'Delivered']),
                        address=f'Address {random.randint(1, 100)}, City',
                        contact_number=f'09{random.randint(100000000, 999999999)}'
                    )
                    session.add(delivery)
                
                # Seed notifications
                notifications = [
                    Notification(title='Low Stock Alert', message='Sinandomeng rice is running low at Marawoy branch', type='Warning'),
                    Notification(title='New Order Received', message='Large order received for Crystal Dinorado', type='Info'),
                    Notification(title='Delivery Completed', message='Delivery to Customer 15 completed successfully', type='Success'),
                    Notification(title='System Maintenance', message='Scheduled maintenance on Sunday 2AM-4AM', type='Info'),
                ]
                session.add_all(notifications)
                
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
        """Default page -> Dashboard"""
        return render_template('Dashboard.html')

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
    # Also handle /inventory (no extension) and case-insensitive names.
    KNOWN_PAGES = {
        'dashboard': 'Dashboard.html',
        'analytics': 'Analytics.html',
        'forecast': 'Forecast.html',
        'regional': 'Regional.html',
        'inventory': 'Inventory.html',
        'sales': 'Sales.html',
        'deliver': 'Deliver.html',
        'purchase': 'Purchase.html',
        'reports': 'Reports.html',
        'user': 'User.html',
        'notifications': 'Notifications.html',
        'settings': 'Settings.html',
        'sidebar': 'Sidebar.html',
    }

    @app.get('/<path:filename>')
    def serve_page_at_root(filename: str):
        # Exact html file path
        key = filename.strip('/').lower()
        if key in KNOWN_PAGES:
            return render_template(KNOWN_PAGES[key])
        # Try known pages without extension and case-insensitive        
        elif filename.lower().endswith('.html'):
            return render_template(filename)
        return jsonify({"error": "Not found"}), 404

    @app.get('/api/ping')
    def ping():
        return jsonify({"message": "pong"})

    # === EXISTING ENDPOINTS ===
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

    # === NEW API ENDPOINTS ===

    # Dashboard Analytics
    @app.get('/api/dashboard/stats')
    def dashboard_stats():
        try:
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    # Total sales today
                    today = datetime.now().date()
                    today_sales = session.query(func.sum(Sales.total_amount)).filter(
                        func.date(Sales.sale_date) == today
                    ).scalar() or 0
                    
                    # Total inventory value
                    total_inventory_value = session.query(func.sum(InventoryItem.stock_kg * InventoryItem.price)).scalar() or 0
                    
                    # Low stock items
                    low_stock_count = session.query(InventoryItem).filter(
                        InventoryItem.availability == 'Low Stock'
                    ).count()
                    
                    # Pending deliveries
                    pending_deliveries = session.query(Delivery).filter(
                        Delivery.status == 'Scheduled'
                    ).count()
                    
                    # Recent sales (last 7 days)
                    week_ago = datetime.now().date() - timedelta(days=7)
                    recent_sales = session.query(Sales).filter(
                        Sales.sale_date >= week_ago
                    ).all()
                    
                    sales_data = []
                    for i in range(7):
                        date = datetime.now().date() - timedelta(days=i)
                        day_sales = sum(s.total_amount for s in recent_sales if s.sale_date == date)
                        sales_data.append({
                            "date": date.isoformat(),
                            "amount": float(day_sales)
                        })
                    
                    return jsonify({
                        "today_sales": float(today_sales),
                        "total_inventory_value": float(total_inventory_value),
                        "low_stock_count": low_stock_count,
                        "pending_deliveries": pending_deliveries,
                        "recent_sales": sales_data[::-1]  # Reverse to show oldest first
                    })
            else:
                # MySQL implementation would go here
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Sales API
    @app.get('/api/sales')
    def get_sales():
        try:
            page = max(int(request.args.get('page', 1)), 1)
            page_size = min(max(int(request.args.get('page_size', 50)), 1), 200)
            offset = (page - 1) * page_size
            
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    q = session.query(Sales)
                    total = q.count()
                    rows = q.order_by(Sales.sale_date.desc()).offset(offset).limit(page_size).all()
                    sales = [
                        {
                            "id": r.id,
                            "branch_id": r.branch_id,
                            "rice_variant": r.rice_variant,
                            "quantity_kg": r.quantity_kg,
                            "price_per_kg": float(r.price_per_kg),
                            "total_amount": float(r.total_amount),
                            "customer_name": r.customer_name,
                            "sale_date": r.sale_date.isoformat() if r.sale_date else None,
                            "created_at": None
                        }
                        for r in rows
                    ]
                    
                    return jsonify({
                        "data": sales,
                        "pagination": {
                            "page": page,
                            "page_size": page_size,
                            "total": total
                        }
                    })
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.post('/api/sales')
    def create_sale():
        try:
            data = request.get_json()
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    sale = Sales(
                        branch_id=data['branch_id'],
                        rice_variant=data['rice_variant'],
                        quantity_kg=data['quantity_kg'],
                        price_per_kg=data['price_per_kg'],
                        total_amount=data['quantity_kg'] * data['price_per_kg'],
                        customer_name=data.get('customer_name'),
                        sale_date=datetime.strptime(data['sale_date'], '%Y-%m-%d').date()
                    )
                    session.add(sale)
                    session.commit()
                    return jsonify({"message": "Sale created successfully", "id": sale.id})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Users API
    @app.get('/api/users')
    def get_users():
        try:
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    rows = session.query(User).order_by(User.id).all()
                    users = [
                        {
                            "id": r.id,
                            "name": r.name,
                            "warehouse_id": r.warehouse_id,
                            "location": r.location,
                            "contact_number": r.contact_number,
                            "role": r.role,
                            "email": r.email,
                            "created_at": None
                        }
                        for r in rows
                    ]
                    return jsonify({"data": users})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.post('/api/users')
    def create_user():
        try:
            data = request.get_json()
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    user = User(
                        name=data['name'],
                        warehouse_id=data['warehouse_id'],
                        location=data['location'],
                        contact_number=data['contact_number'],
                        role=data['role'],
                        email=data.get('email')
                    )
                    session.add(user)
                    session.commit()
                    return jsonify({"message": "User created successfully", "id": user.id})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.put('/api/users/<int:user_id>')
    def update_user(user_id: int):
        try:
            data = request.get_json()
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    user = session.query(User).filter(User.id == user_id).first()
                    if not user:
                        return jsonify({"error": "User not found"}), 404
                    
                    user.name = data['name']
                    user.warehouse_id = data['warehouse_id']
                    user.location = data['location']
                    user.contact_number = data['contact_number']
                    user.role = data['role']
                    user.email = data.get('email')
                    
                    session.commit()
                    return jsonify({"message": "User updated successfully"})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Purchases API
    @app.get('/api/purchases')
    def get_purchases():
        try:
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    rows = session.query(Purchase).order_by(Purchase.purchase_date.desc()).all()
                    purchases = [
                        {
                            "id": r.id,
                            "branch_id": r.branch_id,
                            "rice_variant": r.rice_variant,
                            "quantity_kg": r.quantity_kg,
                            "price_per_kg": float(r.price_per_kg),
                            "total_amount": float(r.total_amount),
                            "supplier_name": r.supplier_name,
                            "purchase_date": r.purchase_date.isoformat() if r.purchase_date else None,
                            "status": r.status,
                            "created_at": None
                        }
                        for r in rows
                    ]
                    return jsonify({"data": purchases})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Deliveries API
    @app.get('/api/deliveries')
    def get_deliveries():
        try:
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    rows = session.query(Delivery).order_by(Delivery.delivery_date).all()
                    deliveries = [
                        {
                            "id": r.id,
                            "branch_id": r.branch_id,
                            "customer_name": r.customer_name,
                            "rice_variant": r.rice_variant,
                            "quantity_kg": r.quantity_kg,
                            "delivery_date": r.delivery_date.isoformat() if r.delivery_date else None,
                            "status": r.status,
                            "address": r.address,
                            "contact_number": r.contact_number,
                            "created_at": None
                        }
                        for r in rows
                    ]
                    return jsonify({"data": deliveries})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Notifications API
    @app.get('/api/notifications')
    def get_notifications():
        try:
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    rows = session.query(Notification).order_by(Notification.created_at.desc()).all()
                    notifications = [
                        {
                            "id": r.id,
                            "title": r.title,
                            "message": r.message,
                            "type": r.type,
                            "is_read": bool(r.is_read),
                            "created_at": None
                        }
                        for r in rows
                    ]
                    return jsonify({"data": notifications})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Analytics API
    @app.get('/api/analytics/sales')
    def sales_analytics():
        try:
            days = int(request.args.get('days', 30))
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    start_date = datetime.now().date() - timedelta(days=days)
                    sales = session.query(Sales).filter(Sales.sale_date >= start_date).all()
                    
                    # Group by rice variant
                    variant_sales = {}
                    for sale in sales:
                        if sale.rice_variant not in variant_sales:
                            variant_sales[sale.rice_variant] = {
                                "total_quantity": 0,
                                "total_amount": 0,
                                "avg_price": 0
                            }
                        variant_sales[sale.rice_variant]["total_quantity"] += sale.quantity_kg
                        variant_sales[sale.rice_variant]["total_amount"] += sale.total_amount
                    
                    # Calculate averages
                    for variant in variant_sales:
                        if variant_sales[variant]["total_quantity"] > 0:
                            variant_sales[variant]["avg_price"] = variant_sales[variant]["total_amount"] / variant_sales[variant]["total_quantity"]
                    
                    return jsonify({"data": variant_sales})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Forecast API (basic implementation)
    @app.get('/api/forecast/demand')
    def demand_forecast():
        try:
            days = int(request.args.get('days', 30))
            if db_url.startswith('sqlite'):
                with Session(engine) as session:
                    # Simple moving average forecast
                    start_date = datetime.now().date() - timedelta(days=90)  # Use 90 days of history
                    sales = session.query(Sales).filter(Sales.sale_date >= start_date).all()
                    
                    # Group by rice variant and date
                    daily_sales = {}
                    for sale in sales:
                        date_str = sale.sale_date.isoformat()
                        if sale.rice_variant not in daily_sales:
                            daily_sales[sale.rice_variant] = {}
                        if date_str not in daily_sales[sale.rice_variant]:
                            daily_sales[sale.rice_variant][date_str] = 0
                        daily_sales[sale.rice_variant][date_str] += sale.quantity_kg
                    
                    # Calculate 7-day moving average for each variant
                    forecasts = {}
                    for variant in daily_sales:
                        dates = sorted(daily_sales[variant].keys())
                        if len(dates) >= 7:
                            recent_7_days = dates[-7:]
                            avg_daily_demand = sum(daily_sales[variant][date] for date in recent_7_days) / 7
                            
                            # Generate forecast for next N days
                            forecast_data = []
                            for i in range(days):
                                forecast_date = datetime.now().date() + timedelta(days=i+1)
                                forecast_data.append({
                                    "date": forecast_date.isoformat(),
                                    "predicted_demand": round(avg_daily_demand, 2),
                                    "confidence_lower": round(avg_daily_demand * 0.8, 2),
                                    "confidence_upper": round(avg_daily_demand * 1.2, 2)
                                })
                            
                            forecasts[variant] = forecast_data
                    
                    return jsonify({"data": forecasts})
            else:
                return jsonify({"error": "MySQL not implemented yet"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return app


# Expose WSGI application for Gunicorn (app:app)
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=True)

