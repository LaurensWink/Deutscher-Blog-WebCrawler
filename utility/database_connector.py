import mysql.connector

def get_db_structure():
    conn = mysql.connector.connect(
        host="localhost",
        user="laurens",
        password="web_crawl",
        database="web_crawl_db"
    )
    if conn.is_connected():
        print("Erfolgreich mit der Datenbank verbunden.")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    for table in cursor.fetchall():
        print(table)

    conn.close()

def creat_db():
    # Verbindung zur MySQL-Datenbank
    conn = mysql.connector.connect(
        host="localhost",
        user="laurens",
        password="web_crawl",
        database="web_crawl_db"
    )


    if conn.is_connected():
            print("Erfolgreich mit der Datenbank verbunden.")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag (
            name VARCHAR(100) PRIMARY KEY,
            UNIQUE(name)
        );
    """)

    conn.commit() 
    cursor.close()
    conn.close()

    print("created db_structur")

creat_db()
