from dungeoncrawler.combat_log import CombatLog
from dungeoncrawler.core.events import AttackResolved
from dungeoncrawler.config import config


def _event(message: str, dmg: int) -> AttackResolved:
    return AttackResolved(message, "A", "B", dmg, 0, 5, 2, False)


def test_combat_log_truncates_buffer():
    log = CombatLog(max_lines=2)
    log.handle_event(_event("first", 1))
    log.handle_event(_event("second", 2))
    log.handle_event(_event("third", 3))
    assert log.lines == ["second", "third"]


def test_combat_log_uses_summary_by_default(monkeypatch):
    monkeypatch.setattr(config, "verbose_combat", False)
    log = CombatLog()
    msg = log.handle_event(_event("A hits B for 3 damage.", 3))
    assert msg == "A hits B for 3 damage."


def test_combat_log_verbose_math(monkeypatch):
    monkeypatch.setattr(config, "verbose_combat", True)
    log = CombatLog()
    msg = log.handle_event(_event("ignored", 3))
    assert "5-2=3" in msg
