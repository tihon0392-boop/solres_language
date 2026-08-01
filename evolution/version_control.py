# evolution/version_control.py
import os
import json
import shutil
from datetime import datetime
from typing import Optional

# Добавляем путь для импортов
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolution.proposal import RuleProposal, ProposalStatus


class LanguageEvolution:
    """
    Управляет эволюцией языка Сольрес.
    Принимает предложения, голосует, обновляет язык.
    """

    def __init__(self, proposals_dir: str = "proposals", backups_dir: str = "backups"):
        self.proposals_dir = proposals_dir
        self.backups_dir = backups_dir

        # Создаём папки
        for directory in [proposals_dir, backups_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        self.proposals: list[RuleProposal] = []
        self._load_all_proposals()

    def _load_all_proposals(self):
        """Загружает все предложения из папки."""
        self.proposals = []
        if not os.path.exists(self.proposals_dir):
            return

        for filename in os.listdir(self.proposals_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.proposals_dir, filename)
                try:
                    prop = RuleProposal.load(filepath)
                    self.proposals.append(prop)
                except Exception as e:
                    print(f"Ошибка загрузки {filename}: {e}")

    def submit_proposal(self, proposal: RuleProposal) -> str:
        """Подаёт новое предложение."""
        filepath = proposal.save(self.proposals_dir)
        self.proposals.append(proposal)
        print(f"📝 Предложение подано: {proposal.description}")
        print(f"   Сохранено в: {filepath}")
        return filepath

    def vote(self, proposal_index: int, up: bool = True):
        """Голосует за предложение по индексу."""
        if 0 <= proposal_index < len(self.proposals):
            self.proposals[proposal_index].vote(up)
            # Обновляем файл
            self.proposals[proposal_index].save(self.proposals_dir)
            action = "👍" if up else "👎"
            print(f"{action} Голос учтён: {self.proposals[proposal_index].description[:50]}")

    def get_top_proposals(self, limit: int = 5) -> list[RuleProposal]:
        """Возвращает предложения с наивысшим рейтингом."""
        active = [p for p in self.proposals if p.status == ProposalStatus.PROPOSED]
        return sorted(active, key=lambda p: p.score(), reverse=True)[:limit]

    def approve_proposal(self, proposal_index: int, lexicon=None) -> bool:
        """
        Одобряет предложение и применяет его к языку.
        Возвращает True, если обновление прошло успешно.
        """
        if not (0 <= proposal_index < len(self.proposals)):
            print("❌ Неверный индекс предложения")
            return False

        prop = self.proposals[proposal_index]

        if prop.status != ProposalStatus.PROPOSED:
            print(f"❌ Предложение уже имеет статус: {prop.status.value}")
            return False

        # Создаём резервную копию перед изменениями
        self._backup_current_state()

        # Применяем изменения
        success = self._apply_proposal(prop, lexicon)

        if success:
            prop.status = ProposalStatus.APPROVED
            prop.save(self.proposals_dir)
            print(f"✅ Предложение ПРИНЯТО: {prop.description}")
            print(f"   Язык Сольрес эволюционировал!")
        else:
            print(f"❌ Не удалось применить предложение")
            # Восстанавливаем из резервной копии
            self._restore_backup()

        return success

    def reject_proposal(self, proposal_index: int):
        """Отклоняет предложение."""
        if 0 <= proposal_index < len(self.proposals):
            self.proposals[proposal_index].status = ProposalStatus.REJECTED
            self.proposals[proposal_index].save(self.proposals_dir)
            print(f"❌ Предложение отклонено: {self.proposals[proposal_index].description[:50]}")

    def _apply_proposal(self, prop: RuleProposal, lexicon=None) -> bool:
        """Применяет предложение к языку."""
        try:
            if prop.category == "word" and lexicon:
                pattern = prop.data.get("pattern")
                meanings = prop.data.get("meanings", [])
                if pattern and meanings:
                    lexicon._add_word(pattern, meanings)
                    return True

            elif prop.category == "grammar":
                # В будущем: обновление grammar.py
                rule_name = prop.data.get("rule_name")
                print(f"   Грамматическое правило '{rule_name}' принято к рассмотрению")
                return True

            elif prop.category == "interval_meaning":
                # Обновление смысла интервала
                interval = prop.data.get("interval")
                new_meaning = prop.data.get("new_meaning")
                print(f"   Интервал {interval} получил новое значение: {new_meaning}")
                return True

            return False

        except Exception as e:
            print(f"Ошибка применения: {e}")
            return False

    def _backup_current_state(self):
        """Создаёт резервную копию текущего состояния языка."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(self.backups_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)

        # Копируем ключевые файлы
        files_to_backup = [
            "language/lexicon.py",
            "language/grammar.py",
        ]

        for filepath in files_to_backup:
            if os.path.exists(filepath):
                dest = os.path.join(backup_path, os.path.basename(filepath))
                shutil.copy2(filepath, dest)

        # Сохраняем словарь в JSON для истории
        if os.path.exists("language/lexicon.py"):
            # Простой бэкап — копируем файл
            pass

        print(f"💾 Резервная копия создана: {backup_name}")

    def _restore_backup(self):
        """Восстанавливает язык из последней резервной копии."""
        backups = sorted(os.listdir(self.backups_dir), reverse=True)
        if not backups:
            print("❌ Нет резервных копий для восстановления")
            return

        latest = backups[0]
        backup_path = os.path.join(self.backups_dir, latest)

        for filename in os.listdir(backup_path):
            src = os.path.join(backup_path, filename)
            dest = os.path.join("language", filename)
            shutil.copy2(src, dest)

        print(f"🔄 Язык восстановлен из: {latest}")

    def show_proposals(self):
        """Показывает все активные предложения."""
        print("\n" + "=" * 60)
        print("📋 АКТИВНЫЕ ПРЕДЛОЖЕНИЯ")
        print("=" * 60)

        active = [p for p in self.proposals if p.status == ProposalStatus.PROPOSED]

        if not active:
            print("   Нет активных предложений.")
            print("   Создайте первое предложение через evolution.submit_proposal()")
            return

        for i, prop in enumerate(active):
            print(f"\n[{i}] {prop.category.upper()}: {prop.description}")
            print(f"    Автор: {prop.author}")
            print(f"    👍 {prop.votes_up} | 👎 {prop.votes_down} | Счёт: {prop.score()}")
            print(f"    Данные: {prop.data}")

    def show_history(self):
        """Показывает историю всех предложений."""
        print("\n" + "=" * 60)
        print("📜 ИСТОРИЯ ЭВОЛЮЦИИ")
        print("=" * 60)

        for i, prop in enumerate(self.proposals):
            status_emoji = {
                "proposed": "📝",
                "approved": "✅",
                "rejected": "❌",
                "deprecated": "🔄"
            }
            emoji = status_emoji.get(prop.status.value, "❓")
            print(f"{emoji} [{prop.category}] {prop.description[:60]}")
            print(f"   Статус: {prop.status.value} | Голоса: +{prop.votes_up}/-{prop.votes_down}")