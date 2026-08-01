# evolution/proposal.py
import json
import os
from datetime import datetime
from enum import Enum


class ProposalStatus(Enum):
    PROPOSED = "proposed"  # Предложено
    APPROVED = "approved"  # Принято
    REJECTED = "rejected"  # Отклонено
    DEPRECATED = "deprecated"  # Устарело (заменено более новым)


class RuleProposal:
    """
    Предложение нового правила или слова для языка Сольрес.
    Любой человек может создать такой файл.
    """

    def __init__(self, author: str, description: str, category: str):
        self.author = author
        self.description = description
        self.category = category  # "word", "grammar", "interval_meaning"
        self.created = datetime.now().isoformat()
        self.status = ProposalStatus.PROPOSED
        self.votes_up = 0
        self.votes_down = 0

        # Данные предложения (зависят от категории)
        self.data = {}

    def set_word_proposal(self, pattern_str: str, meanings: list[str]):
        """Предложение нового слова."""
        self.category = "word"
        self.data = {
            "pattern": pattern_str,
            "meanings": meanings
        }

    def set_grammar_proposal(self, rule_name: str, rule_data: dict):
        """Предложение грамматического правила."""
        self.category = "grammar"
        self.data = {
            "rule_name": rule_name,
            "rule_data": rule_data
        }

    def set_interval_proposal(self, interval: str, new_meaning: str):
        """Предложение нового значения интервала."""
        self.category = "interval_meaning"
        self.data = {
            "interval": interval,
            "new_meaning": new_meaning
        }

    def vote(self, up: bool = True):
        """Голосование за предложение."""
        if up:
            self.votes_up += 1
        else:
            self.votes_down += 1

    def score(self) -> int:
        """Счёт предложения."""
        return self.votes_up - self.votes_down

    def to_dict(self) -> dict:
        """Сериализация для сохранения."""
        return {
            "author": self.author,
            "description": self.description,
            "category": self.category,
            "created": self.created,
            "status": self.status.value,
            "votes_up": self.votes_up,
            "votes_down": self.votes_down,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RuleProposal':
        """Создание предложения из словаря."""
        prop = cls(
            author=data["author"],
            description=data["description"],
            category=data["category"]
        )
        prop.created = data["created"]
        prop.status = ProposalStatus(data["status"])
        prop.votes_up = data["votes_up"]
        prop.votes_down = data["votes_down"]
        prop.data = data["data"]
        return prop

    def save(self, directory: str = "proposals"):
        """Сохраняет предложение в JSON-файл."""
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"{self.category}_{self.created.replace(':', '-')}.json"
        filepath = os.path.join(directory, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

        return filepath

    @classmethod
    def load(cls, filepath: str) -> 'RuleProposal':
        """Загружает предложение из JSON-файла."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __repr__(self):
        return f"Proposal({self.category}: {self.description[:50]}... [{self.status.value}])"