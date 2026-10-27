import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "ssl": {"ssl_mode": "REQUIRED"}
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Check requirements.txt:
Ensure that pymysql and cryptography are listed in your requirements.txt file in your repository so Vercel installs them during build time.

Redeploy:
Go to your Deployments tab on Vercel, click the three dots (...) on your latest deployment, and click Redeploy.

Once it finishes building, your app will successfully link to your Aiven MySQL database and load your pages without any 500 errors!


def init_db(force_reseed=False):
    """Initializes tables and seeds initial data across all categories."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS order_items")
        cursor.execute("DROP TABLE IF EXISTS bills")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS menu_items")
        cursor.execute("DROP TABLE IF EXISTS categories")
        cursor.execute("DROP TABLE IF EXISTS inventory")
        cursor.execute("DROP TABLE IF EXISTS suppliers")
        cursor.execute("DROP TABLE IF EXISTS staff")
        cursor.execute("DROP TABLE IF EXISTS feedback")
        cursor.execute("DROP TABLE IF EXISTS customers")
        cursor.execute("DROP TABLE IF EXISTS tables")

    # 1. Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            icon TEXT
        );
    """)

    # 2. Menu Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (category_id) ON DELETE CASCADE
        );
    """)

    # 3. Tables / Floor Map Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tables (
            table_id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number TEXT NOT NULL UNIQUE,
            capacity INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('available', 'occupied', 'reserved')),
            floor_area TEXT DEFAULT 'Main Dining Hall'
        );
    """)

    # 4. Customers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 5. Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            table_number TEXT DEFAULT 'Table 1',
            total_amount REAL NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('incoming', 'preparing', 'delivered')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 6. Order Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES menu_items (item_id) ON DELETE CASCADE
        );
    """)

    # 7. Bills / Invoices Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            customer_name TEXT,
            subtotal REAL NOT NULL,
            tax REAL NOT NULL,
            discount REAL NOT NULL,
            grand_total REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
        );
    """)

    # 8. Staff / Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            phone TEXT,
            salary REAL NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 9. Feedback Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            rating INTEGER NOT NULL,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 10. Suppliers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT
        );
    """)

    # 11. Inventory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            reorder_level INTEGER NOT NULL,
            supplier_id INTEGER,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON DELETE SET NULL
        );
    """)

    # Check if we need to migrate/reseed with authentic Kerala Cuisine data
    check_kerala = cursor.execute("SELECT COUNT(*) FROM menu_items WHERE name LIKE '%Biriyani%' OR name LIKE '%Porotta%'").fetchone()[0]
    if force_reseed or check_kerala == 0:
        # Clear existing demo data to ensure consistent Kerala cuisine dataset
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM bills")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM menu_items")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM inventory")
        cursor.execute("DELETE FROM suppliers")
        cursor.execute("DELETE FROM staff")
        cursor.execute("DELETE FROM feedback")
        cursor.execute("DELETE FROM customers")
        cursor.execute("DELETE FROM tables")

        # 1. Categories Seed (Breakfast, Afternoon, Evening Snacks, Drinks & Desserts)
        categories_data = [
            ("Breakfast", "🌅"),
            ("Afternoon Meals & Biriyani", "🍛"),
            ("Evening Snacks", "☕"),
            ("Drinks & Desserts", "🍹")
        ]
        cursor.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", categories_data)

        # 2. Kerala Menu Items Seed
        # Category 1 = Breakfast, Category 2 = Afternoon/Lunch, Category 3 = Evening Snacks, Category 4 = Drinks & Desserts
        kerala_items = [
            # --- BREAKFAST ---
            (
                "Kerala Puttu & Kadala Curry",
                "Steamed cylindrical rice cakes layered with grated coconut, served with rich spicy black chickpea curry.",
                80.00,
                "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=400&q=80",
                1
            ),
            (
                "Malabar Porotta with Beef Roast",
                "Multi-layered crispy flaky Malabar flatbread paired with tender slow-roasted Kerala spiced beef roast.",
                140.00,
                "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=400&q=80",
                1
            ),
            (
                "Appam with Chicken Stew",
                "Soft, fluffy fermented rice hoppers with crispy lacy borders, paired with rich coconut milk chicken stew.",
                110.00,
                "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=400&q=80",
                1
            ),
            (
                "Crispy Ghee Roast Dosa",
                "Golden thin crepe roasted in pure desi ghee, served with hot Kerala vegetable sambar and coconut chutney.",
                75.00,
                "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=400&q=80",
                1
            ),
            (
                "Idiyappam with Coconut Milk",
                "Delicate steamed rice string hoppers served with sweet cardamom-infused coconut milk and vegetable kurma.",
                70.00,
                "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=400&q=80",
                1
            ),

            # --- AFTERNOON MEALS & BIRIYANI ---
            (
                "Thalassery Chicken Biriyani",
                "Authentic Malabar Dum Biriyani cooked with aromatic Jeerakasala/Kaima rice, tender spiced chicken, fried onions, cashews, raisins, and raita.",
                190.00,
                "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=400&q=80",
                2
            ),
            (
                "Arabian Chicken Kuzhi Mandi",
                "Smoky coal-cooked authentic Mandi rice with succulent spiced chicken quarter, fresh tomato sahawiq salsa, and garlic toum.",
                220.00,
                "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?auto=format&fit=crop&w=400&q=80",
                2
            ),
            (
                "Kerala Traditional Sadhya Oonu",
                "Steamed Kerala Matta red rice served with Sambar, Avial, Thoran, Pulissery, Mango Pickle, Crispy Pappadam and Payasam on banana leaf.",
                120.00,
                "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?auto=format&fit=crop&w=400&q=80",
                2
            ),
            (
                "Karimeen Pollichathu Fish Meals",
                "Fresh pearl spot fish marinated in shallot-chilli masala, wrapped and slow-tava roasted in fresh banana leaves, with Matta rice.",
                260.00,
                "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80",
                2
            ),
            (
                "Kuttanadan Duck Roast & Ghee Rice",
                "Rich peppery duck roast prepared with coconut slivers and Kuttanad spices, served with fragrant Kerala Nei Choru.",
                210.00,
                "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=400&q=80",
                2
            ),

            # --- EVENING SNACKS ---
            (
                "Pazham Pori & Malabar Beef Fry",
                "Sweet golden Kerala ripe plantain fritters served classic Malabar street-food style alongside spicy pepper beef roast.",
                65.00,
                "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=400&q=80",
                3
            ),
            (
                "Parippu Vada & Sukhiyan Combo",
                "Two crunchy spiced chana dal vadas and sweet golden jaggery green-gram dumplings served hot with green chillies.",
                35.00,
                "https://images.unsplash.com/photo-1541518763669-27fef04b14ea?auto=format&fit=crop&w=400&q=80",
                3
            ),
            (
                "Malabar Chicken Kozhi Ada",
                "Traditional crescent-shaped pastry filled with seasoned shredded chicken masala and fresh herbs, crisped golden brown.",
                40.00,
                "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=400&q=80",
                3
            ),
            (
                "Thalassery Sweet Unnakaya",
                "Spindle-shaped steamed banana delicacy stuffed with sweetened coconut, scrambled egg, dry fruits, and fragrant cardamom.",
                40.00,
                "https://images.unsplash.com/photo-1505253758473-96b3015f21c9?auto=format&fit=crop&w=400&q=80",
                3
            ),
            (
                "Sulaimani & Cardamom Dum Tea",
                "Brewed Malabar black tea infused with mint, cloves & fresh lime, served alongside piping-hot frothy cardamom milk tea.",
                25.00,
                "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=400&q=80",
                3
            ),

            # --- DRINKS & DESSERTS ---
            (
                "Special Kulukki Sarbath",
                "Signature Kerala shaken iced lemonade with soaked basil seeds (sabja), fresh green chillies, ginger, and mint.",
                45.00,
                "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=400&q=80",
                4
            ),
            (
                "Royal Ada Pradhaman Payasam",
                "Royal festive dessert simmered with tender rice flakes, dark coconut jaggery, thick coconut milk, and ghee-roasted cashews.",
                70.00,
                "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=400&q=80",
                4
            ),
            (
                "Tender Coconut Elaneer Pudding",
                "Refreshing, velvety chilled pudding prepared from fresh sweet Kerala tender coconut pulp and condensed milk.",
                75.00,
                "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=400&q=80",
                4
            )
        ]
        cursor.executemany("""
            INSERT INTO menu_items (name, description, price, image_url, category_id)
            VALUES (?, ?, ?, ?, ?)
        """, kerala_items)

        # 3. Tables Seed
        tables_data = [
            ("Table 1", 4, "available", "Courtyard Heritage"),
            ("Table 2", 6, "occupied", "Royal Dining Hall"),
            ("Table 3", 8, "reserved", "Family AC Suite"),
            ("Table 4", 2, "available", "Verandah Garden"),
            ("Table 5", 4, "occupied", "Main Dining Hall"),
            ("Table 6", 10, "available", "Executive Banquet")
        ]
        cursor.executemany("""
            INSERT INTO tables (table_number, capacity, status, floor_area)
            VALUES (?, ?, ?, ?)
        """, tables_data)

        # 4. Customers Seed
        customers_data = [
            ("Dr. Rahul Menon", "98471-88990", "rahul.menon@keralahealth.org", "Menon Villa, Panampilly Nagar, Kochi"),
            ("Amina Basheer", "94462-77112", "amina.basheer@calicutnet.in", "Rose Cottage, Beach Road, Kozhikode"),
            ("Siddharth Varma", "98954-33221", "sid.varma@trivandrumtech.com", "Flat 4B, Skyline Apts, Kowdiar, Thiruvananthapuram"),
            ("Niveditha Pillai", "97440-66554", "niveditha.pillai@alappuzha.org", "Palace Road, Alappuzha")
        ]
        cursor.executemany("""
            INSERT INTO customers (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """, customers_data)

        # 5. Suppliers Seed
        suppliers_data = [
            ("Wayanad Jeerakasala Rice Traders", "Haris Rahman", "94471-22334", "orders@wayanadrice.com", "Kalpetta, Wayanad"),
            ("Idukki Spice Valley Co.", "Thomas Joseph", "98470-11223", "spices@idukkiagro.in", "Kumily, Idukki"),
            ("Cochin Harbor Fresh Seafoods", "Antony Xavier", "98950-33445", "seafoods@cochinharbor.in", "Vypeen, Kochi"),
            ("Malabar Fresh Farm Poultry & Meats", "Musthafa K.", "97455-44556", "sales@malabarmeats.com", "Koduvally, Kozhikode"),
            ("Kera Natural Coconut Oils & Ghee", "Sujith Kumar", "94463-55667", "info@keranaturals.in", "Changanassery, Kottayam")
        ]
        cursor.executemany("""
            INSERT INTO suppliers (name, contact_person, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
        """, suppliers_data)

        # 6. Inventory Seed
        inventory_data = [
            ("Jeerakasala Kaima Rice", 85, "kg", 25, 1),
            ("Kerala Matta Red Rice", 120, "kg", 30, 1),
            ("Idukki Green Cardamom & Cloves", 14, "kg", 5, 2),
            ("Fresh Chicken Cuts", 38, "kg", 15, 4),
            ("Fresh Pearl Spot (Karimeen)", 9, "kg", 15, 3),   # Low stock warning
            ("Pure Desi Ghee", 22, "kg", 10, 5),
            ("Kerala Kera Coconut Oil", 45, "L", 15, 5),
            ("Ripe Nendran Bananas", 12, "kg", 20, 1),        # Low stock warning
            ("Black Chickpeas (Kadala)", 30, "kg", 10, 1)
        ]
        cursor.executemany("""
            INSERT INTO inventory (item_name, quantity, unit, reorder_level, supplier_id)
            VALUES (?, ?, ?, ?, ?)
        """, inventory_data)

        # 7. Staff Seed
        staff_data = [
            ("Chef Moideen K.", "Master Malabar Head Chef", "98470-55101", 58000.00),
            ("Chef Sujith Pillai", "Traditional Sadhya & Curry Specialist", "98470-55102", 48000.00),
            ("Fahad Manzil", "Restaurant General Operations Manager", "98470-55103", 52000.00),
            ("Anjali Nair", "Front Desk & Floor Supervisor", "98470-55104", 32000.00),
            ("Vishnu Raj", "Senior Dining Captain & Sommelier", "98470-55105", 26000.00)
        ]
        cursor.executemany("""
            INSERT INTO staff (full_name, role, phone, salary)
            VALUES (?, ?, ?, ?)
        """, staff_data)

        # 8. Initial Orders Seed
        orders_data = [
            ("Dr. Rahul Menon", "Table 2", 470.00, "preparing"),
            ("Walk-in Guest", "Table 5", 295.00, "incoming"),
            ("Amina Basheer", "Table 1", 495.00, "delivered")
        ]
        cursor.executemany("""
            INSERT INTO orders (customer_name, table_number, total_amount, status)
            VALUES (?, ?, ?, ?)
        """, orders_data)

        # 9. Order Items Seed
        # Order 1: 2x Thalassery Biriyani (item 6: 190.00) + 2x Kulukki Sarbath (item 16: 45.00) = 470
        # Order 2: 1x Arabian Kuzhi Mandi (item 7: 220.00) + 1x Elaneer Pudding (item 18: 75.00) = 295
        # Order 3: 3x Malabar Porotta & Beef (item 2: 140.00) + 3x Sulaimani Tea (item 15: 25.00) = 495
        order_items_data = [
            (1, 6, 2, 190.00),
            (1, 16, 2, 45.00),
            (2, 7, 1, 220.00),
            (2, 18, 1, 75.00),
            (3, 2, 3, 140.00),
            (3, 15, 3, 25.00)
        ]
        cursor.executemany("""
            INSERT INTO order_items (order_id, item_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
        """, order_items_data)

        # 10. Initial Bills Seed (Order 3 completed)
        # Subtotal: 495.00, Tax (5% GST): 24.75, Discount: 0.00, Grand Total: 519.75
        cursor.execute("""
            INSERT INTO bills (order_id, customer_name, subtotal, tax, discount, grand_total, payment_method, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (3, "Amina Basheer", 495.00, 24.75, 0.00, 519.75, "UPI / GPay", "Paid"))

        # 11. Feedback Seed
        feedback_data = [
            ("Dr. Rahul Menon", 5, "The Thalassery Biriyani with Jeerakasala rice and date pickle tasted completely authentic! Exceptional table hospitality."),
            ("Amina Basheer", 5, "Crispy golden Pazham Pori with spicy Malabar Beef Roast was heavenly. Warm Kerala ambiance and lightning-fast service."),
            ("Siddharth Varma", 4, "Loved the Karimeen Pollichathu in banana leaf and the Elaneer pudding dessert. Highly recommended for family dining.")
        ]
        cursor.executemany("""
            INSERT INTO feedback (customer_name, rating, comments)
            VALUES (?, ?, ?)
        """, feedback_data)

    conn.commit()
    conn.close()


# ================= API ENDPOINTS =================


# 1. EXECUTIVE DASHBOARD STATS
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    active_customers = cursor.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    reservations_today = cursor.execute("SELECT COUNT(*) FROM tables WHERE status = 'reserved'").fetchone()[0]
    fulfilled_orders = cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'delivered'").fetchone()[0]
    revenue_result = cursor.execute("SELECT SUM(grand_total) FROM bills WHERE payment_status = 'Paid'").fetchone()[0]
    total_revenue = float(revenue_result) if revenue_result else 0.0
    total_menu_items = cursor.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    low_stock_count = cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= reorder_level").fetchone()[0]

    conn.close()
    return jsonify({
        "active_customers": active_customers,
        "reservations_today": reservations_today,
        "fulfilled_orders": fulfilled_orders,
        "total_revenue": total_revenue,
        "total_menu_items": total_menu_items,
        "low_stock_count": low_stock_count
    })


# 2. CATEGORIES
@app.route("/api/categories", methods=["GET"])
def get_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY category_id ASC").fetchall()
    conn.close()
    return jsonify([dict(c) for c in categories])


# 3. MENU ITEMS
@app.route("/api/menu", methods=["GET"])
def get_menu():
    conn = get_db_connection()
    query = """
        SELECT m.item_id, m.name, m.description, m.price, m.image_url, m.category_id, c.name as category_name, c.icon as category_icon
        FROM menu_items m
        LEFT JOIN categories c ON m.category_id = c.category_id
        ORDER BY m.category_id ASC, m.item_id ASC
    """
    items = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])


@app.route("/api/menu", methods=["POST"])
def add_menu_item():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    try:
        price = float(data.get("price", 0.0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid price"}), 400

    image_url = data.get("image_url") or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80"
    category_id = int(data.get("category_id", 1))

    if not name or price <= 0:
        return jsonify({"error": "Valid dish name and positive price are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, description, price, image_url, category_id) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, image_url, category_id),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Menu item created successfully", "item_id": new_id}), 201


@app.route("/api/menu/<int:item_id>", methods=["DELETE"])
def delete_menu_item(item_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM menu_items WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Menu item deleted successfully"})


# 4. TABLES (FLOOR SEATING MAP)
@app.route("/api/tables", methods=["GET"])
def get_tables():
    conn = get_db_connection()
    tables = conn.execute("SELECT * FROM tables ORDER BY table_id ASC").fetchall()
    conn.close()
    return jsonify([dict(t) for t in tables])


@app.route("/api/tables/<int:table_id>/status", methods=["PUT"])
def update_table_status(table_id):
    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ["available", "occupied", "reserved"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE tables SET status = ? WHERE table_id = ?",
        (new_status, table_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Table status updated successfully"})


# 5. ORDERS (KANBAN DISPATCH PIPELINE)
@app.route("/api/orders", methods=["GET"])
def get_orders():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders ORDER BY order_id DESC").fetchall()
    result = []
    for o in orders:
        o_dict = dict(o)
        items = conn.execute(
            """
            SELECT oi.quantity, oi.unit_price, m.name 
            FROM order_items oi
            JOIN menu_items m ON oi.item_id = m.item_id
            WHERE oi.order_id = ?
            """,
            (o["order_id"],),
        ).fetchall()
        o_dict["items"] = [dict(it) for it in items]
        result.append(o_dict)
    conn.close()
    return jsonify(result)


@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ["incoming", "preparing", "delivered"]:
        return jsonify({"error": "Invalid order status"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        (new_status, order_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Order status updated successfully"})


# 6. CUSTOMERS DIRECTORY
@app.route("/api/customers", methods=["GET"])
def get_customers():
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers ORDER BY customer_id DESC").fetchall()
    conn.close()
    return jsonify([dict(c) for c in customers])


@app.route("/api/customers", methods=["POST"])
def add_customer():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()

    if not name or not phone:
        return jsonify({"error": "Name and phone number are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
        (name, phone, email, address),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Customer registered successfully", "customer_id": new_id}), 201


# 7. STAFF & EMPLOYEES
@app.route("/api/staff", methods=["GET"])
def get_staff():
    conn = get_db_connection()
    staff_members = conn.execute("SELECT * FROM staff ORDER BY staff_id ASC").fetchall()
    conn.close()
    return jsonify([dict(s) for s in staff_members])


@app.route("/api/staff", methods=["POST"])
def add_staff():
    data = request.get_json() or {}
    full_name = (data.get("full_name") or "").strip()
    role = (data.get("role") or "").strip()
    phone = (data.get("phone") or "").strip()
    try:
        salary = float(data.get("salary", 0.0))
    except (ValueError, TypeError):
        salary = 0.0

    if not full_name or not role:
        return jsonify({"error": "Full name and role are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO staff (full_name, role, phone, salary) VALUES (?, ?, ?, ?)",
        (full_name, role, phone, salary),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Staff member added successfully", "staff_id": new_id}), 201


@app.route("/api/staff/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM staff WHERE staff_id = ?", (staff_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Staff member removed successfully"})


# 8. SUPPLIERS
@app.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    conn = get_db_connection()
    suppliers = conn.execute("SELECT * FROM suppliers ORDER BY supplier_id ASC").fetchall()
    conn.close()
    return jsonify([dict(s) for s in suppliers])


@app.route("/api/suppliers", methods=["POST"])
def add_supplier():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    contact_person = (data.get("contact_person") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()

    if not name or not phone:
        return jsonify({"error": "Supplier name and phone are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)",
        (name, contact_person, phone, email, address),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Supplier added successfully", "supplier_id": new_id}), 201


# 9. INVENTORY & STOCK REPLENISHMENT
@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    conn = get_db_connection()
    query = """
        SELECT i.*, s.name as supplier_name 
        FROM inventory i
        LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
        ORDER BY i.quantity ASC
    """
    items = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])


@app.route("/api/inventory", methods=["POST"])
def add_inventory_item():
    data = request.get_json() or {}
    item_name = (data.get("item_name") or "").strip()
    try:
        quantity = int(data.get("quantity", 0))
        reorder_level = int(data.get("reorder_level", 10))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid quantity or reorder level"}), 400

    unit = (data.get("unit") or "kg").strip()
    supplier_id = data.get("supplier_id") or None

    if not item_name:
        return jsonify({"error": "Stock item name is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (item_name, quantity, unit, reorder_level, supplier_id) VALUES (?, ?, ?, ?, ?)",
        (item_name, quantity, unit, reorder_level, supplier_id),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Inventory item added successfully", "inventory_id": new_id}), 201


@app.route("/api/inventory/<int:inventory_id>/restock", methods=["PUT"])
def restock_inventory(inventory_id):
    data = request.get_json() or {}
    try:
        add_qty = int(data.get("quantity", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid restock quantity"}), 400

    if add_qty <= 0:
        return jsonify({"error": "Restock quantity must be positive"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE inventory SET quantity = quantity + ? WHERE inventory_id = ?",
        (add_qty, inventory_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Inventory restocked successfully"})


@app.route("/api/inventory/<int:inventory_id>", methods=["DELETE"])
def delete_inventory_item(inventory_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM inventory WHERE inventory_id = ?", (inventory_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Inventory item removed successfully"})


# 10. BILLS & AUTOMATED BILLING GENERATION
@app.route("/api/bills", methods=["GET"])
def get_bills():
    conn = get_db_connection()
    bills = conn.execute("SELECT * FROM bills ORDER BY bill_id DESC").fetchall()
    conn.close()
    return jsonify([dict(b) for b in bills])


@app.route("/api/bills/<int:bill_id>", methods=["GET"])
def get_bill_detail(bill_id):
    conn = get_db_connection()
    bill = conn.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,)).fetchone()
    if not bill:
        conn.close()
        return jsonify({"error": "Bill not found"}), 404

    b_dict = dict(bill)
    items = conn.execute(
        """
        SELECT oi.quantity, oi.unit_price, m.name 
        FROM order_items oi
        JOIN menu_items m ON oi.item_id = m.item_id
        WHERE oi.order_id = ?
        """,
        (b_dict["order_id"],),
    ).fetchall()
    b_dict["items"] = [dict(it) for it in items]
    conn.close()
    return jsonify(b_dict)


@app.route("/api/bills/generate", methods=["POST"])
def generate_bill():
    data = request.get_json() or {}
    customer_name = (data.get("customer_name") or "Walk-in Guest").strip()
    table_number = (data.get("table_number") or "Table 1").strip()
    items = data.get("items", [])
    payment_method = (data.get("payment_method") or "UPI / Cash").strip()
    try:
        discount = float(data.get("discount", 0.0))
    except (ValueError, TypeError):
        discount = 0.0

    if not items:
        return jsonify({"error": "No items provided for bill generation"}), 400

    subtotal = sum(float(item.get("price", 0)) * int(item.get("qty", 1)) for item in items)
    tax = round(subtotal * 0.05, 2)  # 5% GST on Restaurant Service
    grand_total = max(0.0, round(subtotal + tax - discount, 2))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Order record in DB
    cursor.execute(
        "INSERT INTO orders (customer_name, table_number, total_amount, status) VALUES (?, ?, ?, ?)",
        (customer_name, table_number, grand_total, "incoming"),
    )
    order_id = cursor.lastrowid

    # Create Order Items records
    for item in items:
        item_name = item.get("name")
        qty = int(item.get("qty", 1))
        price = float(item.get("price", 0))

        menu_item = cursor.execute("SELECT item_id FROM menu_items WHERE name = ?", (item_name,)).fetchone()
        item_id = menu_item[0] if menu_item else None

        if item_id:
            cursor.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, item_id, qty, price),
            )

    # Create Bill record in DB
    cursor.execute(
        """
        INSERT INTO bills (order_id, customer_name, subtotal, tax, discount, grand_total, payment_method, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, customer_name, subtotal, tax, discount, grand_total, payment_method, "Paid"),
    )
    bill_id = cursor.lastrowid

    # Register customer if not already present
    existing_cust = cursor.execute("SELECT customer_id FROM customers WHERE name = ?", (customer_name,)).fetchone()
    if not existing_cust and customer_name != "Walk-in Guest":
        cursor.execute(
            "INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)",
            (customer_name, "N/A", "Dine-in Customer"),
        )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Bill generated successfully",
        "bill_id": bill_id,
        "order_id": order_id,
        "subtotal": subtotal,
        "tax": tax,
        "discount": discount,
        "grand_total": grand_total
    }), 201


# 11. FEEDBACK SENTIMENTS
@app.route("/api/feedback", methods=["GET"])
def get_feedback():
    conn = get_db_connection()
    feedbacks = conn.execute("SELECT * FROM feedback ORDER BY feedback_id DESC").fetchall()
    conn.close()
    return jsonify([dict(f) for f in feedbacks])


@app.route("/api/feedback", methods=["POST"])
def add_feedback():
    data = request.get_json() or {}
    customer_name = (data.get("customer_name") or "Anonymous").strip()
    try:
        rating = int(data.get("rating", 5))
    except (ValueError, TypeError):
        rating = 5
    comments = (data.get("comments") or "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (customer_name, rating, comments) VALUES (?, ?, ?)",
        (customer_name, rating, comments),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Feedback submitted successfully"}), 201


# 12. BUSINESS ANALYTICS & AUDIT EXPORT (DBMS prefix removed)
@app.route("/api/reports/summary", methods=["GET"])
def get_reports_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    total_revenue = cursor.execute("SELECT SUM(grand_total) FROM bills WHERE payment_status = 'Paid'").fetchone()[0] or 0.0
    total_bills = cursor.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
    total_inventory_items = cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    low_stock_count = cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= reorder_level").fetchone()[0]
    total_suppliers = cursor.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
    total_staff = cursor.execute("SELECT COUNT(*) FROM staff").fetchone()[0]

    conn.close()
    return jsonify({
        "total_revenue": total_revenue,
        "total_bills": total_bills,
        "total_inventory_items": total_inventory_items,
        "low_stock_count": low_stock_count,
        "total_suppliers": total_suppliers,
        "total_staff": total_staff
    })


@app.route("/api/reports/export", methods=["GET"])
def export_reports():
    conn = get_db_connection()
    bills = [dict(b) for b in conn.execute("SELECT * FROM bills ORDER BY bill_id DESC").fetchall()]
    orders = [dict(o) for o in conn.execute("SELECT * FROM orders ORDER BY order_id DESC").fetchall()]
    inventory = [dict(i) for i in conn.execute("SELECT * FROM inventory").fetchall()]
    conn.close()
    return jsonify({
        "bills": bills,
        "orders": orders,
        "inventory": inventory
    })


# 13. DEMO SEED RESET
@app.route("/api/reset_kerala_demo", methods=["POST"])
def reset_kerala_demo():
    init_db(force_reseed=True)
    return jsonify({"message": "Database successfully reseeded with authentic Kerala Cuisine demo data!"})


# 14. SERVE FRONTEND AT ROOT URL
@app.route("/")
def serve_root():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    init_db(force_reseed=False)
    print("Database initialized successfully. Server starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
