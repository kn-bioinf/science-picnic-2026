from src.screens.welcome_screen import WelcomeScreen
from src.screens.end_screen     import EndScreen
from src.screens.ranking_screen import RankingScreen
from src.levels.level1.controller import Level1Controller
# from src.levels.level2.controller import Level2Controller


class GameManager:
    """
    Zarządza aktywnymi scenami i przejściami między nimi. Na razie mamy tylko 1 poziom.

    Przepływ:
        WelcomeScreen -> Level1Controller -> EndScreen
    """

    WELCOME = "welcome"
    LEVEL1  = "level1"
    # LEVEL2  = "level2"
    END     = "end"
    RANKING = "ranking"

    def __init__(self, screen, state):
        self.screen = screen
        self.state  = state
        self._scene = None
        self.transition_to(self.WELCOME)

    def transition_to(self, scene_id: str) -> None:
        scenes = {
            self.WELCOME: lambda: WelcomeScreen(self.screen, self.state, self),
            self.LEVEL1:  lambda: Level1Controller(self.screen, self.state, self),
            # self.LEVEL2:  lambda: Level2Controller(self.screen, self.state, self),
            self.END:     lambda: EndScreen(self.screen, self.state, self),
            self.RANKING: lambda: RankingScreen(self.screen, self.state, self),
        }
        self._scene = scenes[scene_id]()

    def handle_event(self, e): self._scene.handle_event(e)
    def update(self, dt):       self._scene.update(dt)
    def draw(self):             self._scene.draw()
