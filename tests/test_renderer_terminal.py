from dungeoncrawler.ui.terminal import Renderer
from dungeoncrawler.core.events import AttackResolved


def test_renderer_outputs_event_messages():
    lines = []
    r = Renderer(output_func=lines.append)
    event = AttackResolved("hit", "A", "B", 1, 0)
    r.render_events([event])
    assert lines == ["hit"]
