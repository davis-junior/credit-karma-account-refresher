import sqlite3


def create_tables(cursor: sqlite3.Cursor):
    sql = """
    --begin-sql
        CREATE TABLE IF NOT EXISTS creditkarma (
            username TEXT,
            account TEXT,
            status TEXT,
            info TEXT,
            timestamp_added TIMESTAMP
        )
    --end-sql
    """

    cursor.execute(sql)


def add_db_record(
    cursor: sqlite3.Cursor, username: str, account: str, status: str, info: str
):
    sql = """
    --begin-sql
        INSERT INTO creditkarma
        (username, account, status, info, timestamp_added)
        VALUES
        (?, ?, ?, ?, datetime(current_timestamp, 'localtime'))
    --end-sql
    """

    cursor.execute(
        sql,
        (
            username,
            account,
            status,
            info,
        ),
    )
