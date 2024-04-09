from typing import List, Dict


class Page:
    def __init__(self, database_id: int, user_id: int, url: str, short: str, visits: int):
        self.id: int = database_id
        self.user_id: int = user_id
        self.url: str = url
        self.short: str = short
        self.visits: int = visits

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'url': self.url,
            'short': self.short,
            'visits': self.visits
        }

    @staticmethod
    def from_database(values: List) -> 'Page':
        return Page(*values)
