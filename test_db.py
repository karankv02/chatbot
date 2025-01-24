from db_config import get_connection

# Test the connection
connection = get_connection()
if connection:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM suppliers;")
    rows = cursor.fetchall()

    print("Suppliers Data:")
    for row in rows:
        print(row)

    cursor.close()
    connection.close()
else:
    print("Connection failed!")
