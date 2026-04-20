import sqlite3
from datetime import datetime
import hashlib

DB_PATH = "erp_system.db"

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def authenticate(username, password):
    """Authenticate user credentials."""
    conn = get_db_connection()
    if not conn:
        return False
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hashed_password)
    ).fetchone()
    
    conn.close()
    return user is not None

def log_audit(username, action, details):
    """Log an audit trail entry."""
    conn = get_db_connection()
    if conn:
        timestamp = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO audit_log (username, action, details, timestamp) VALUES (?, ?, ?, ?)",
            (username, action, details, timestamp)
        )
        conn.commit()
        conn.close()

def get_audit_logs(limit=100):
    """Retrieve audit logs."""
    conn = get_db_connection()
    if conn:
        logs = conn.execute(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return logs
    return []

def init_database():
    """Initialize database tables."""
    conn = get_db_connection()
    if conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audit log table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP NOT NULL
            )
        """)
        
        # Products/Inventory table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                cost REAL NOT NULL,
                quantity INTEGER DEFAULT 0,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Orders table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Order items table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create default admin user if not exists
        admin_exists = conn.execute(
            "SELECT COUNT(*) FROM users WHERE username = 'admin'"
        ).fetchone()[0]
        
        if not admin_exists:
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", hashed_password, "admin")
            )
        
        conn.commit()
        conn.close()
        return True
    return False
