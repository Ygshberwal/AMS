import sqlite3

def inspect_db():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(table[0])
    
    # Query example: Display contents of the 'students' table
    cursor.execute("SELECT * FROM students;")
    rows = cursor.fetchall()
    print("\nContents of 'students' table:")
    for row in rows:
        print(row)
    
    conn.close()

inspect_db()
