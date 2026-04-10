import mysql.connector

passwords = ['Navtej@2006', 'root', 'password', 'Navtej@123', 'root123', 'admin', 'Navtej2006', 'mysql', '']
found = False
for p in passwords:
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=p,
            connect_timeout=2
        )
        if conn.is_connected():
            print(f"PASSWORD_MATCH_SUCCESS: {p}")
            conn.close()
            found = True
            break
    except mysql.connector.Error as e:
        print(f"PASSWORD_MATCH_FAILED: {p} (Error Code: {e.errno})")
    except Exception as e:
        print(f"PASSWORD_MATCH_FAILED: {p} (Unexpected: {e})")

if not found:
    print("PASSWORD_MATCH_NONE_FOUND")
