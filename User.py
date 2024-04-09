from typing import List, Dict


class User:
    def __init__(self, database_id: int, username: str, password: bytes):
        self.database_id: int = database_id
        self.username: str = username
        self.password: bytes = password

    def to_json(self) -> Dict:
        return {
            'id': self.database_id,
            'username': self.username
        }
