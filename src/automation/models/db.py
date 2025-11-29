from PySide6.QtSql import QSqlDatabase, QSqlQuery


def connect_to_database(db_name: str) -> bool:
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_name)
    if not db.open():
        return False
    return True


def create_table():
    query = QSqlQuery()
    query.exec_("""
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform INTEGER NOT NULL,
            cookies TEXT,
            icon_raw TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            UNIQUE (name, platform)
        )
        """)

    query.exec_("""
        CREATE TABLE IF NOT EXISTS UserGroup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)

    query.exec_("""
        CREATE TABLE IF NOT EXISTS UserUserGroup (
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, group_id),
            FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES UserGroup(id) ON DELETE CASCADE
        )
        """)

    query.exec_("""
        CREATE TABLE IF NOT EXISTS Record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status INTEGER NOT NULL,
            record_type INTEGER DEFAULT 0
        )
    """)

    query.exec_("""
        CREATE TABLE IF NOT EXISTS Employee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status INTEGER Not NULL, 
            phone_number TEXT NOT NULL
        )
    """)

    query.exec_("""
        CREATE TABLE IF NOT EXISTS Position (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            permission INTEGER NOT NULL
        )
    """)

    query.exec_("""
        CREATE TABLE IF NOT EXISTS EmployeePosition (
            employee_id INTEGER NOT NULL,
            position_id INTEGER NOT NULL,
            PRIMARY KEY (employee_id, position_id),
            FOREIGN KEY (employee_id) REFERENCES Employee(id) ON DELETE CASCADE,
            FOREIGN KEY (position_id) REFERENCES Position(id) ON DELETE CASCADE
        )
        """)
