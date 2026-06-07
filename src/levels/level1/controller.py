from src.levels.level1.stage1 import Stage1
from src.levels.level1.stage2 import Stage2
from src.levels.level1.stage3 import Stage3


class Level1Controller:
    """
    Poziom 1 – kinezy na mikrotubuli.
    Kolejnosc etapow: Stage1 -> Stage2 -> Stage3 -> Koniec (lub poziom drugi)
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
        self._active = Stage3(self.screen, self.state, next_fn=self._after3)

    def _after3(self, score=0):
        self.state.score += score
        self.manager.transition_to(self.manager.END)

    def handle_event(self, e): self._active.handle_event(e)
    def update(self, dt):       self._active.update(dt)
    def draw(self):             self._active.draw()
