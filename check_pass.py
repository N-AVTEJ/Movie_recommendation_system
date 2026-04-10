import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Navtej@2006',
        auth_plugin='mysql_native_password'
    )
    print("SUCCESS")
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
