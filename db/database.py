import sqlite3 as sqlite
from typing import Dict, List
from enum import Enum


class DatabaseResponse(Enum):
    ERROR = 0
    SUCCESS = 1
    NOT_UNIQUE = 2
    NO_CHANGES = 3


def dict_factory(c, row):
    d = {}
    for idx, col in enumerate(c.description):
        d[col[0]] = row[idx]
    return d


def insert(table: str, values: Dict[str, str]):
    if len(values) == 0:
        return False

    query_values: str = ", ".join(["?"] * len(values))
    sql: str = f"INSERT INTO {table} ({",".join(values.keys())}) VALUES ({query_values})"

    try:
        res = cursor.execute(sql, tuple(values.values()))
        connection.commit()
    except sqlite.IntegrityError:
        connection.rollback()
        return DatabaseResponse.NOT_UNIQUE

    return res


def select_one(table: str, values: Dict[str, str], columns: List[str] = ["*"]):
    if len(values) > 0:
        where_values: List[str] = []
        for key in values.keys():
            where_values.append(f"{key} = ?")
        where: str = "WHERE "+" AND ".join(where_values)
    else:
        where: str = ""

    sql: str = f"SELECT {",".join(columns)} FROM {table} {where}"
    return connection.cursor().execute(sql, tuple(values.values())).fetchone()


def select_many(table: str, values: Dict[str, str], columns: List[str] = ["*"]):
    if len(values) > 0:
        where_values: List[str] = []
        for key in values.keys():
            where_values.append(f"{key} = ?")
        where: str = "WHERE "+" AND ".join(where_values)
    else:
        where: str = ""

    sql: str = f"SELECT {",".join(columns)} FROM {table} {where}"
    return cursor.execute(sql, tuple(values.values())).fetchall()


def update(table: str, database_id: int, values: Dict[str, object]) -> DatabaseResponse:
    if len(values) <= 0:
        return DatabaseResponse.NO_CHANGES

    update_values: List[str] = []
    for key in values.keys():
        update_values.append(f"{key} = ?")
    query_values: List[str] = list(values.values())
    query_values.append(str(database_id))
    sql: str = f"UPDATE {table} SET {",".join(update_values)} WHERE id=?"
    cursor.execute(sql, tuple(query_values))
    connection.commit()
    return DatabaseResponse.SUCCESS


connection = sqlite.connect("url_shortener.db", check_same_thread=False)

with open('./db/schema.sql') as f:
    print("Executing schema.sql")
    connection.executescript(f.read())

connection.row_factory = dict_factory
cursor = connection.cursor()
