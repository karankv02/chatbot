import mysql.connector
from mysql.connector import Error
import json

# Connect to MySQL Database
try:
    conn = mysql.connector.connect(
        host='localhost',       # Database host, usually 'localhost'
        user='karan_kv',            # MySQL username (e.g., 'root' or another user)
        password='march0203',  # MySQL password (replace with your actual password)
        database='ai_chatbot_db'  # Database name
    )
    if conn.is_connected():
        print("Successfully connected to the database")

    cursor = conn.cursor()

    # Step 1: Create products and suppliers tables (only if they do not exist)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        brand VARCHAR(100),
        price DECIMAL(10, 2),
        category VARCHAR(50),
        description TEXT,
        supplier_id INT,
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        contact_info JSON,
        product_categories_offered JSON
    );
    ''')

    # Step 2: Insert some sample data into suppliers table
    suppliers_data = [
        ('Supplier A', '{"email": "contact@suppliera.com", "phone": "123-456-7890"}', '["Laptops", "Electronics"]'),
        ('ABC Electronics', '{"email": "abc@electronics.com", "phone": "+1234567890"}', '["Laptops", "Smartphones", "Accessories"]'),
        ('XYZ Suppliers', '{"email": "xyz@suppliers.com", "phone": "+0987654321"}', '["Laptops", "Tablets"]')
    ]

    cursor.executemany('''
    INSERT INTO suppliers (name, contact_info, product_categories_offered) 
    VALUES (%s, %s, %s)
    ''', suppliers_data)

    # Step 3: Insert sample data into products table
    products_data = [
        ('Laptop A', 'Brand A', 499.99, 'Laptops', 'High performance laptop', 1),
        ('Laptop B', 'Brand B', 299.99, 'Laptops', 'Budget-friendly laptop', 2),
        ('Smartphone A', 'Brand C', 199.99, 'Smartphones', 'Smartphone with great camera', 2),
        ('Tablet A', 'Brand D', 399.99, 'Tablets', 'Lightweight and portable tablet', 3)
    ]

    cursor.executemany('''
    INSERT INTO products (name, brand, price, category, description, supplier_id) 
    VALUES (%s, %s, %s, %s, %s, %s)
    ''', products_data)

    # Commit the transaction
    conn.commit()

    # Step 4: Fetch and display the data from the products and suppliers tables
    cursor.execute('''
    SELECT p.name AS product_name, p.brand, p.price, p.category, p.description, s.name AS supplier_name, s.contact_info
    FROM products p
    INNER JOIN suppliers s ON p.supplier_id = s.id;
    ''')

    result = cursor.fetchall()
    for row in result:
        print(f"Product: {row[0]} | Brand: {row[1]} | Price: {row[2]} | Category: {row[3]} | Description: {row[4]} | Supplier: {row[5]} | Contact: {json.loads(row[6])}")

except Error as e:
    print(f"Error: {e}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("Connection closed.")
