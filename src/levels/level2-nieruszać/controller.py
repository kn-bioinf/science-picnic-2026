# TODO: Poziom 2 – bialko transbłonowe (inne etapy, inne minigry).
# Dodaj tutaj swoje stage'y wzorujac sie na level1/controller.py.

from src.levels.level2.stage1 import Stage1
from src.levels.level2.stage2 import Stage2


class Level2Controller:
    """
    Poziom 2 – przykladowo: bialko transbłonowe.
    Kolejnosc etapow: Stage1 -> Stage2 -> Koniec
    """

    def __init__(self, screen, state, manager):
        self.screen  = screen
        self.state   = state
        self.manager = manager
        self._active = Stage1(screen, state, next_fn=self._after1)

    def _after1(self, score=0):
        self.state.score += score
        self._active = Stage2(self.screen, self.state, next_fn=self._after2)

    def _after2(self, score=0):
        self.state.score += score
        self.manager.transition_to(self.manager.END)

    def handle_event(self, e): self._active.handle_event(e)
    def update(self, dt):       self._active.update(dt)
    def draw(self):             self._active.draw()
