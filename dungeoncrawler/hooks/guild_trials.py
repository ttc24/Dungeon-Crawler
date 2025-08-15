from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Hook tracking guild trial completion."""

    def on_objective_check(self, state, floor):
        """Objective met when any two trials are completed."""
        return len(getattr(state.game, "completed_trials", set())) >= 2
