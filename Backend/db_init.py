import sqlite3

def init_db():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys= 1")
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS students (
            rollno Text PRIMARY KEY,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attendance (
            s_rollno TEXT,
            c_id TEXT,
            i_id INTEGER,
            lecture_date DATE,
            status INTEGER,
            FOREIGN KEY(s_rollno) REFERENCES students(rollno),
            FOREIGN KEY(c_id) REFERENCES courses(id),
            FOREIGN KEY(i_id) REFERENCES instructors(id)
        );
            
        CREATE TABLE IF NOT EXISTS studying (
            s_rollno INTEGER,
            c_id TEXT,
            FOREIGN KEY(c_id) REFERENCES courses(id),
            FOREIGN KEY(s_rollno) REFERENCES students(rollno)
        );

        CREATE TABLE IF NOT EXISTS teaches (
            c_id TEXT,
            i_id INTEGER,
            FOREIGN KEY(i_id) REFERENCES instructors(id),
            FOREIGN KEY(c_id) REFERENCES courses(id)
        );
        CREATE TABLE IF NOT EXISTS attendance (
            s_rollno INTEGER,
            c_id TEXT,
            i_id INTEGER,
            FOREIGN KEY(s_rollno) REFERENCES students(rollno),
            FOREIGN KEY(c_id) REFERENCES courses(id),
            FOREIGN KEY(i_id) REFERENCES instructors(id)
        );
                
                        
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")