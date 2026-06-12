import pygame
import src.config as config
from src.levels.level1.stage1 import Stage1
from src.levels.level1.stage2 import Stage2
from src.levels.level1.stage3 import Stage3

_STAGES = {1: Stage1, 2: Stage2, 3: Stage3}


class Level1Controller:
    """
    Poziom 1 - kinezyna na mikrotubuli.

    mode='full'   : etapy 1 -> 2 -> 3, sumuje wyniki, na końcu manager.finish_full.
    mode='single' : tylko wskazany etap, po przejściu manager.finish_single (-> menu).

    Dodatkowo: dwa dyskretne przyciski adminowe w prawym dolnym rogu okna,
    aktywne przez cały czas rozgrywki (także na ekranie przegranej/wygranej,
    dopóki nie klikniemy „Dalej"):
        Restart - zaczyna od nowa BIEŻĄCY etap (w trybie pełnym zachowuje wyniki
                  wcześniej ukończonych etapów),
        Quit    - wychodzi z rozgrywki do menu.
    """

    def __init__(self, screen, state, manager, mode="full", stage=1):
        self.screen = screen
        self.state = state
        self.manager = manager
        self.mode = mode
        self._scores = {}
        # małe, dyskretne przyciski adminowe (pozycja liczona przy rysowaniu)
        self._btn_restart = pygame.Rect(0, 0, 96, 28)
        self._btn_quit = pygame.Rect(0, 0, 96, 28)
        self._start(stage if mode == "single" else 1)

    def _start(self, n):
        self._current = n
        self._active = _STAGES[n](self.screen, self.state, next_fn=self._on_done)

    def _restart(self):
        """Restart bieżącego etapu od początku. Wyniki wcześniej ukończonych
        etapów (self._scores) zostają nietknięte - wracamy tylko do tego etapu,
        w którym właśnie jesteśmy."""
        self._start(self._current)

    def _on_done(self, score=0):
        self._scores[self._current] = int(score)
        if self.mode == "single":
            self.manager.finish_single(self._current, int(score))
        elif self._current < 3:
            self._start(self._current + 1)
        else:
            self.manager.finish_full(self._scores)

    # ---------------------------------------------------- przyciski adminowe
    def _layout_admin(self):
        w, h = config.get_size()
        self._btn_quit.bottomright = (w - 12, h - 12)
        self._btn_restart.bottomright = (
            w - 12 - self._btn_quit.width - 8, h - 12)

    def _draw_admin(self):
        self._layout_admin()
        for rect, label in ((self._btn_restart, "Restart"),
                            (self._btn_quit, "Quit")):
            pill = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(pill, (28, 38, 66, 95), pill.get_rect(),
                             border_radius=6)
            pygame.draw.rect(pill, (255, 255, 255, 70), pill.get_rect(), 1,
                             border_radius=6)
            self.screen.blit(pill, rect.topleft)
            lbl = config.font(14).render(label, True, (225, 232, 245))
            self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    # ------------------------------------------------------------ pętla sceny
    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self._layout_admin()
            if self._btn_restart.collidepoint(e.pos):
                self._restart()
                return
            if self._btn_quit.collidepoint(e.pos):
                self.manager.transition_to(self.manager.MENU)
                return
        self._active.handle_event(e)

    def update(self, dt):
        self._active.update(dt)

    def draw(self):
        self._active.draw()
        self._draw_admin()
