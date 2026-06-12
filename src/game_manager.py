from src.screens.menu_screen import MenuScreen
from src.screens.end_screen import EndScreen
from src.screens.ranking_screen import RankingScreen
from src.screens.knowledge_screen import KnowledgeScreen
from src.levels.level1.controller import Level1Controller


class GameManager:
    """
    Zarządza scenami i przejściami.

    Sceny statyczne: MENU, RANKING, KNOWLEDGE, END.
    Rozgrywka: Level1Controller w trybie 'full' (etapy 1->2->3) lub 'single'.
    """

    MENU = "menu"
    RANKING = "ranking"
    KNOWLEDGE = "knowledge"
    END = "end"

    def __init__(self, screen, state):
        self.screen = screen
        self.state = state
        self._scene = None
        self.transition_to(self.MENU)

    # -------------------------------------------------------- sceny statyczne
    def transition_to(self, scene_id):
        scenes = {
            self.MENU:      lambda: MenuScreen(self.screen, self.state, self),
            self.RANKING:   lambda: RankingScreen(self.screen, self.state, self),
            self.KNOWLEDGE: lambda: KnowledgeScreen(self.screen, self.state, self),
            self.END:       lambda: EndScreen(self.screen, self.state, self),
        }
        self._scene = scenes[scene_id]()

    # -------------------------------------------------------------- rozgrywka
    def play_full(self):
        self.state.reset_run()
        self._scene = Level1Controller(self.screen, self.state, self, mode="full")

    def play_stage(self, n):
        self.state.reset_run()
        self._scene = Level1Controller(self.screen, self.state, self,
                                       mode="single", stage=n)

    def finish_full(self, stage_scores):
        """Koniec pełnej gry: zapisz total + każdy etap, pokaż ekran końca."""
        self.state.stage_scores = dict(stage_scores)
        self.state.score = sum(stage_scores.values())
        for n, sc in stage_scores.items():
            self.state.save_score(f"stage{n}", sc)
        self.state.save_score("total", self.state.score)
        self.transition_to(self.END)

    def finish_single(self, n, score):
        """Koniec pojedynczego etapu: zapisz tylko ranking etapu, wróć do menu."""
        self.state.save_score(f"stage{n}", score)
        self.transition_to(self.MENU)

    # -------------------------------------------------------------- pętla
    def handle_event(self, e): self._scene.handle_event(e)
    def update(self, dt):      self._scene.update(dt)
    def draw(self):            self._scene.draw()
