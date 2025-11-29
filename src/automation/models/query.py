from PySide6.QtCore import QDateTime
from PySide6.QtSql import QSqlQuery

from utils import Platform
from utils.constant import EmpployeeType, PublishType
from utils.struct import Employee, Position, Record


def get_users_from_user_ids(user_ids: list[int]):
    placeholders = ",".join("?" * len(user_ids))
    query = QSqlQuery()
    query.prepare(f"""
        SELECT id, name, platform, cookies, icon_raw, is_active 
        FROM User 
        WHERE id IN ({placeholders})
    """)

    for user_id in user_ids:
        query.addBindValue(user_id)

    if not query.exec():
        print(f"Query error: {query.lastError().text()}")
        return []

    users = []
    while query.next():
        users.append(
            dict(
                id=query.value("id"),
                name=query.value("name"),
                platform=query.value("platform"),
                cookies=query.value("cookies"),
                icon_raw=query.value("icon_raw"),
                is_active=bool(query.value("is_active")),
            )
        )

    return users


def check_if_usergroup_exists(group_name: str) -> bool:
    query = QSqlQuery()
    query.prepare("""
        SELECT id
        FROM UserGroup
        WHERE name = ? 
    """)
    query.addBindValue(group_name)
    query.exec()

    return query.next()  # Returns True if a row is found, False otherwise


def check_if_user_exists(name: str, platform: int) -> bool:
    query = QSqlQuery()
    query.prepare("""
        SELECT id
        FROM User
        WHERE name = ? AND platform = ?
    """)
    query.addBindValue(name)
    query.addBindValue(platform)
    query.exec()

    return query.next()  # Returns True if a row is found, False otherwise


def insert_records(records: list):
    query = QSqlQuery()
    current_datetime = QDateTime.currentDateTime()
    timestamp = current_datetime.toSecsSinceEpoch()
    query.prepare("""
        INSERT INTO Record (timestamp, user_id, title, content, status)
        VALUES (:timestamp, :user_id, :title, :content, :status)
        """)

    for record in records:
        query.bindValue(":timestamp", timestamp)
        query.bindValue(":user_id", record["user_id"])
        query.bindValue(":title", record["title"])
        query.bindValue(":content", record["content"])
        query.bindValue(":status", record["status"])

        if not query.exec():
            print(
                f"Failed to insert record: {record}, error: {query.lastError().text()}"
            )


def update_user_state(user_id: int, is_active: int) -> bool:
    query = QSqlQuery()
    query.prepare("""
        UPDATE User
        SET is_active = ?
        WHERE id = ?
    """)
    query.addBindValue(is_active)
    query.addBindValue(user_id)
    query_success = query.exec()
    if not query_success:
        print(f"Query execution failed: {query.lastError().text()}")
    else:
        print("successful")
    return query_success


def update_cookies(name: str, platform: int, new_cookies: str):
    query = QSqlQuery()
    query.prepare("""
        UPDATE User
        SET cookies = ?, is_active = ?
        WHERE name = ? AND platform = ?
    """)
    query.addBindValue(new_cookies)
    query.addBindValue(1)
    query.addBindValue(name)
    query.addBindValue(platform)
    query_success = query.exec()

    if not query_success:
        print(f"Query execution failed: {query.lastError().text()}")
    else:
        return query.lastInsertId()


def get_all_users_with_active():
    query = QSqlQuery()
    query.prepare("""
        SELECT id, platform, cookies
        FROM User
        WHERE is_active = 1
    """)
    active_users = []
    if query.exec():
        while query.next():
            active_users.append(
                dict(
                    user_id=query.value(0),
                    platform=query.value(1),
                    cookies=query.value(2),
                )
            )
    else:
        print(f"Failed to execute query: {query.lastError().text()}")
    return active_users


def get_all_users_for_tests():
    query = QSqlQuery()
    query.prepare("""
        SELECT id, platform, cookies
        FROM User
    """)
    users = []
    if query.exec():
        while query.next():
            users.append(
                dict(
                    user_id=query.value(0),
                    platform=query.value(1),
                    cookies=query.value(2),
                )
            )
    else:
        print(f"Failed to execute query: {query.lastError().text()}")
    return users


def get_user_by_id(idx: int):
    query = QSqlQuery()
    query.prepare("""
        SELECT id, name, platform, cookies, is_active, icon_raw
        FROM User Where id = ?
    """)
    query.addBindValue(idx)
    if not query.exec():
        print("Select failed:", query.lastError().text())
        return None
    if query.next():
        user = {
            "id": query.value(0),
            "name": query.value(1),
            "platform": query.value(2),
            "cookies": query.value(3),
            "is_active": query.value(4),
            "icon_bytes": query.value(5),
        }
        return user


def add_users_to_group(user_ids: list[int], group_id: int):
    query = QSqlQuery()
    for user_id in user_ids:
        query.prepare("""
            INSERT OR IGNORE INTO UserUserGroup (user_id, group_id)
            VALUES (:user_id, :group_id)
        """)
        query.bindValue(":user_id", user_id)
        query.bindValue(":group_id", group_id)
        if not query.exec():
            print(
                f"Failed to insert user-group association for user ID {user_id}:",
                query.lastError().text(),
            )


def get_all_users():
    query = QSqlQuery()
    query_success = query.exec("""
        SELECT id, name, platform, cookies, is_active, icon_raw
        FROM User
    """)
    if not query_success:
        print(f"Query execution failed: {query.lastError().text()}")
        return []
    users = []
    while query.next():
        user = {
            "id": query.value(0),
            "name": query.value(1),
            "platform": query.value(2),
            "cookies": query.value(3),
            "is_active": query.value(4),
            "icon_raw": query.value(5),
        }

        users.append(user)
    return users


def get_users_in_group(group_id):
    query = QSqlQuery()
    query.prepare("""
        SELECT User.id, User.name, User.platform, User.cookies, User.icon_raw, User.is_active
        FROM User
        JOIN UserUserGroup ON User.id = UserUserGroup.user_id
        WHERE UserUserGroup.group_id = :group_id
    """)
    query.bindValue(":group_id", group_id)

    if not query.exec():
        print(f"Query execution failed: {query.lastError().text()}")
        return []

    users = []
    while query.next():
        user = {
            "id": query.value(0),
            "name": query.value(1),
            "platform": query.value(2),
            "cookies": query.value(3),
            "icon_raw": query.value(4),
            "is_active": query.value(5),
        }
        users.append(user)

    return users


def get_users_in_platform(platform: Platform):
    query = QSqlQuery()
    query.prepare("""
        SELECT id, name, platform, cookies, icon_raw, is_active
        FROM User
        WHERE platform LIKE :platform
    """)
    query.bindValue(":platform", platform.value)
    if not query.exec():
        print(f"Query execution failed: {query.lastError().text()}")
        return []

    users = []
    while query.next():
        user = {
            "id": query.value(0),
            "name": query.value(1),
            "platform": query.value(2),
            "cookies": query.value(3),
            "icon_raw": query.value(4),
            "is_active": query.value(5),
        }
        users.append(user)

    return users


def search_users_by_name(keyword):
    query = QSqlQuery()
    query.prepare("""
        SELECT id, name, platform, cookies, icon_raw, is_active
        FROM User
        WHERE name LIKE :keyword
    """)
    query.bindValue(":keyword", f"%{keyword}%")

    if not query.exec():
        print(f"Query execution failed: {query.lastError().text()}")
        return []

    users = []
    while query.next():
        user = {
            "id": query.value(0),
            "name": query.value(1),
            "platform": query.value(2),
            "cookies": query.value(3),
            "icon_raw": query.value(4),
            "is_active": query.value(5),
        }
        users.append(user)

    return users


def get_all_groups():
    query = QSqlQuery()
    query_success = query.exec("""
        SELECT id, name FROM UserGroup
    """)
    if not query_success:
        print(f"Query execution failed: {query.lastError().text()}")
        return []
    user_groups = []
    while query.next():
        group = {
            "id": query.value(0),
            "name": query.value(1),
        }

        user_groups.append(group)
    return user_groups


def delete_groups(group_ids: list[int]):
    query = QSqlQuery()
    for group_id in group_ids:
        query.prepare("""
                DELETE FROM UserUserGroup
                WHERE group_id = :group_id
            """)
        query.bindValue(":group_id", group_id)
        if not query.exec():
            print(
                f"Failed to delete associated rows in UserUserGroup for group ID {group_id}:",
                query.lastError().text(),
            )


def delete_user(user_id):
    query = QSqlQuery()
    query.prepare("DELETE FROM User WHERE id = :user_id")
    query.bindValue(":user_id", user_id)

    if query.exec():
        print(f"User with id {user_id} deleted successfully.")
    else:
        print(f"Failed to delete user: {query.lastError().text()}")


def remove_groups_from_user(user_id, group_ids):
    query = QSqlQuery()
    for group_id in group_ids:
        query.prepare("""
            DELETE FROM UserUserGroup
            WHERE user_id = :user_id AND group_id = :group_id
        """)

        query.bindValue(":user_id", user_id)
        query.bindValue(":group_id", group_id)
        if query.exec():
            print(
                f"Groups {group_id} removed from user with id {user_id} successfully."
            )
        else:
            print(f"Failed to remove groups: {query.lastError().text()}")


def add_user_group(group_name) -> int | None:
    query = QSqlQuery()
    query.prepare("""
        INSERT INTO UserGroup (name)
        VALUES (:name)
        """)
    query.bindValue(":name", group_name)

    if query.exec():
        group_id = query.lastInsertId()
        print(f"User group '{group_name}' added with ID {group_id}")
        return group_id
    else:
        print(f"Failed to add user group '{group_name}'")
        return None


def query_users_with_groups(usergroup_id: int = None) -> list[dict]:
    if usergroup_id is None:
        stmt = """
        SELECT User.id, User.name, User.platform, User.is_active, User.icon_raw, UserGroup.name AS group_name, UserGroup.id AS group_id

        FROM User
        LEFT JOIN UserUserGroup ON User.id = UserUserGroup.user_id
        LEFT JOIN UserGroup ON UserUserGroup.group_id = UserGroup.id
        ORDER BY User.id, UserGroup.name
        """
    else:
        stmt = f"""
        SELECT User.id, User.name, User.platform, User.is_active, User.icon_raw, UserGroup.name AS group_name, UserGroup.id AS group_id
        FROM User
        LEFT JOIN UserUserGroup ON User.id = UserUserGroup.user_id
        LEFT JOIN UserGroup ON UserUserGroup.group_id = UserGroup.id
        WHERE UserGroup.id = {usergroup_id}
        ORDER BY User.id, UserGroup.name
        """

    query = QSqlQuery()
    query_success = query.exec(stmt)

    if not query_success:
        print(f"Query execution failed: {query.lastError().text()}")

    users_with_groups = {}

    while query.next():
        user_id = query.value(0)
        username = query.value(1)
        platform = query.value(2)
        is_active = query.value(3)
        icon_str = query.value(4)
        group_name = query.value(5)
        group_id = query.value(6)

        if user_id not in users_with_groups:
            users_with_groups[user_id] = {
                "user_id": user_id,
                "username": username,
                "platform": platform,
                "icon_str": icon_str,
                "is_active": is_active,
                "groups": [],
            }
        if len(group_name) != 0:
            users_with_groups[user_id]["groups"].append((group_id, group_name))
    return list(users_with_groups.values())


def get_records_from_time(start_time: int, end_time: int):
    query_str = """
        SELECT Record.id, Record.timestamp, Record.title, Record.status, User.name, User.platform, User.icon_raw
        FROM Record
        JOIN User ON Record.user_id = User.id
        WHERE Record.timestamp BETWEEN :start_time AND :end_time
    """

    query = QSqlQuery()
    query.prepare(query_str)
    query.bindValue(":start_time", start_time)
    query.bindValue(":end_time", end_time)

    records = []
    if query.exec():
        while query.next():
            records.append(
                dict(
                    record_id=query.value(0),
                    timestamp=query.value(1),
                    title=query.value(2),
                    status=query.value(3),
                    username=query.value(4),
                    platform=query.value(5),
                    icon_raw=query.value(6),
                )
            )
    return records


# query for statistics


def get_records_for_stats(start_time: int, end_time: int) -> list[Record]:
    query_str = """
        SELECT Record.id, Record.timestamp, Record.title, Record.status, User.name, User.platform, User.icon_raw, Record.record_type
        FROM Record
        JOIN User ON Record.user_id = User.id
        WHERE Record.timestamp BETWEEN :start_time AND :end_time
    """

    query = QSqlQuery()
    query.prepare(query_str)
    query.bindValue(":start_time", start_time)
    query.bindValue(":end_time", end_time)

    records = []
    if query.exec():
        while query.next():
            records.append(
                Record(
                    id=query.value(0),
                    timestamp=query.value(1),
                    title=query.value(2),
                    status=query.value(3),
                    username=query.value(4),
                    platform=Platform.from_value_to_platform(query.value(5)),
                    record_type=PublishType.from_value(query.value(7)),
                    icon_raw=query.value(6),
                )
            )
    else:
        print("Query failed:", query.lastError().text())
    return records


# query for employee


def get_all_employees() -> list[Employee]:
    query = QSqlQuery()

    sql = """
    SELECT Employee.id, Employee.name, Employee.phone_number, Employee.status, Position.id AS position_id,
           Position.title, Position.permission
    FROM Employee
    LEFT JOIN EmployeePosition ON Employee.id = EmployeePosition.employee_id
    LEFT JOIN Position ON EmployeePosition.position_id = Position.id
    """
    if not query.exec(sql):
        print("Query failed:", query.lastError().text())
        return []
    else:
        employees_dict = {}

        while query.next():
            employee_id = query.value("id")
            employee_name = query.value("name")
            employee_phone = query.value("phone_number")
            position_id = query.value("position_id")
            position_title = query.value("title")
            position_permission = query.value("permission")
            status = EmpployeeType.from_value(query.value("status"))

            if employee_id not in employees_dict:
                employees_dict[employee_id] = Employee(
                    id=employee_id,
                    name=employee_name,
                    phone_number=employee_phone,
                    status=status,
                )

            if position_title is not None:
                position = Position(
                    id=position_id, title=position_title, permission=position_permission
                )
                employees_dict[employee_id].positions.append(position)

        employees_list = list(employees_dict.values())
    return employees_list


def get_all_positions() -> list[Position]:
    query = QSqlQuery()

    sql = "SELECT id, title, permission FROM Position"

    if not query.exec(sql):
        print("Query failed:", query.lastError().text())
        return []
    else:
        positions = []

        while query.next():
            position_id = query.value("id")
            title = query.value("title")
            permission = query.value("permission")
            positions.append(
                Position(id=position_id, title=title, permission=permission)
            )
        return positions


def insert_position(title: str, permission: int) -> bool:
    sql = f"INSERT INTO Position (title, permission) VALUES ('{title}', '{permission}')"

    query = QSqlQuery()
    if not query.exec(sql):
        print("Insert failed:", query.lastError().text())
        return False
    return True


def delete_position(position_id) -> bool:
    query = QSqlQuery()
    query.prepare("DELETE FROM Position WHERE id = :id")
    query.bindValue(":id", position_id)
    if not query.exec():
        print("Delete failed:", query.lastError().text())
        return False
    return True


def update_position(position_id, new_permission: int) -> bool:
    query = QSqlQuery()
    query.prepare("UPDATE Position SET permission = :permission WHERE id = :id")
    query.bindValue(":id", position_id)
    query.bindValue(":permission", new_permission)
    if not query.exec():
        print("Update failed:", query.lastError().text())
        return False
    return True


def update_employ(employee_id, status: int) -> bool:
    query = QSqlQuery()
    query.prepare("UPDATE Employee SET status = :status WHERE id = :id")
    query.bindValue(":id", employee_id)
    query.bindValue(":status", status)
    if not query.exec():
        print("Update failed:", query.lastError().text())
        return False
    return True


def insert_positions_to_employee(employee_id: int, position_ids: list[int]) -> bool:
    query = QSqlQuery()
    for pos_id in position_ids:
        query.prepare(
            "INSERT INTO EmployeePosition (employee_id, position_id) VALUES (?, ?)"
        )
        query.addBindValue(employee_id)
        query.addBindValue(pos_id)
        if not query.exec():
            print("Insert employee-position failed:", query.lastError().text())
            return False
    return True


def delete_employee_position(employee_id, position_ids: list[int]) -> bool:
    query = QSqlQuery()

    for pos_id in position_ids:
        query.prepare(
            "DELETE FROM EmployeePosition WHERE employee_id = ? AND position_id = ?"
        )
        query.addBindValue(employee_id)
        query.addBindValue(pos_id)

        if not query.exec():
            print("Delete failed:", query.lastError().text())
            return False

    return True


def test_add_employees():
    query = QSqlQuery()
    positions = [
        ("Position A", "110110110"),
        ("Position B", "001100110"),
        ("Position C", "101010101"),
        ("Position D", "010101010"),
    ]

    for title, perm in positions:
        query.prepare("INSERT INTO Position (title, permission) VALUES (?, ?)")
        query.addBindValue(title)
        query.addBindValue(perm)
        if not query.exec():
            print("Insert position failed:", query.lastError().text())

    employees = [
        ("John Doe", "1234567890", 1),
        ("Jane Smith", "0987654321", 2),
        ("Alex Johnson", "4567891230", 2),
        ("Sam Wilson", "7890123456", 3),
    ]

    for name, phone, status in employees:
        query.prepare(
            "INSERT INTO Employee (name, phone_number, status) VALUES (?, ?, ?)"
        )
        query.addBindValue(name)
        query.addBindValue(phone)
        query.addBindValue(status)
        if not query.exec():
            print("Insert employee failed:", query.lastError().text())

    assignments = [
        (1, 1),
        (1, 2),
        (2, 2),
        (3, 3),
        (3, 4),
    ]

    for emp_id, pos_id in assignments:
        query.prepare(
            "INSERT INTO EmployeePosition (employee_id, position_id) VALUES (?, ?)"
        )
        query.addBindValue(emp_id)
        query.addBindValue(pos_id)
        if not query.exec():
            print("Insert employee-position failed:", query.lastError().text())
