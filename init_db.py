import sqlite3

def init_db():
    # إنشاء أو الاتصال بقاعدة البيانات
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. جدول الحسابات (Accounts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            game_id TEXT NOT NULL,
            status TEXT DEFAULT 'Stopped',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. جدول المهام (Tasks)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            task_name TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("تم إنشاء قاعدة البيانات database.db والجداول بنجاح! 🚀")

if __name__ == '__main__':
    init_db()