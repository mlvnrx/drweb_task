import os
import sqlite3

from typing import Any

from werkzeug.security import generate_password_hash


class Database:
    _instance = None

    def __new__(cls, path: os.path):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize(path)
        return cls._instance

    def _initialize(self, path: str):
        self.path = path

    @property
    def connection(self):
        return sqlite3.connect(self.path)

    def execute(
        self,
        statement: str,
        parameters: list[Any] | None = None,
        fetchone=False,
        fetchall=False,
        commit=False,
    ) -> Any | None:
        if not parameters:
            parameters = tuple()

        with self.connection as con:
            cursor = con.cursor()
            cursor.execute(statement, parameters)

            if commit:
                con.commit()
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()

    @staticmethod
    def format_args(statement: str, parameters: dict) -> tuple[Any]:
        parameters = {k: v for k, v in parameters if v is not None}
        statement += " "
        statement += " AND ".join([f"{item} = ?" for item in parameters])
        return statement, tuple(parameters.values())

    def __del__(self):
        self.connection.close()


db = Database("users.sqlite3")


def get_user(username: str) -> dict[str, str] | None:
    data = db.execute(
        "SELECT * FROM users WHERE username=?;", [username], fetchone=True
    )
    if not data:
        return None
    return {
        "username": data[0],
        "password": data[1]
    }


def add_user(username: str, password: str) -> None:
    pswd_hash = generate_password_hash(password)

    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?);",
        [username, pswd_hash],
        commit=True,
    )
