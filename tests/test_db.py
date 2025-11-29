import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtSql import QSqlDatabase, QSqlQuery
import requests


def create_connection():
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('mydatabase.db')

    if not db.open():
        print("Unable to open database")
        return False

    return True


def create_table():
    query = QSqlQuery()
    query.exec(
        "CREATE TABLE IF NOT EXISTS my_table (id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB)"
    )


def insert_bytes():
    byte_array = bytearray("Test binary data", 'utf-8')
    print(byte_array)
    query = QSqlQuery()
    query.prepare("INSERT INTO my_table (data) VALUES (?)")
    query.bindValue(0, byte_array)

    if not query.exec():
        print("Error inserting bytes:", query.lastError().text())
    else:
        print("Bytes inserted successfully.")


def get_blob_length(record_id):
    query = QSqlQuery()
    query.prepare("SELECT data FROM my_table WHERE id = ?")
    query.addBindValue(record_id)

    if not query.exec():
        print("Select failed:", query.lastError().text())
    else:
        if query.next():
            retrieved_data = query.value(0)
            print("Retrieved data:", retrieved_data)

    return None


def fetch_image_as_bytes(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")
        return None


app = QApplication(sys.argv)

if create_connection():
    create_table()

    # Fetch the image as bytes
    insert_bytes()

    # Assume you know the id of the record you just inserted, here we're assuming it's 1
    record_id = 1
    length = get_blob_length(record_id)
    if length is not None:
        print(f"The length of the BLOB with id {record_id} is {length} bytes.")

app.exit()
