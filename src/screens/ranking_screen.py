import pygame
import src.config as config
from src.game_state import GameState


class RankingScreen:
    """Minimalny ekran rankingu: wyświetla `ranking.json` i przycisk powrotu."""

    def __init__(self, screen, state, manager):
        self.screen = screen
        self.state = state
        self.manager = manager
        self._btn = pygame.Rect(0, 0, 160, 40)
        self._rows = GameState.load_ranking()

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self._btn.collidepoint(e.pos):
            self.manager.transition_to(self.manager.WELCOME)

    def update(self, dt):
        pass

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)
        title = config.font(36, bold=True).render("Ranking", True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(w//2, 60)))

        # list
        y = 110
        for i, r in enumerate(self._rows):
            txt = f"{i+1}. {r.get('name','-')} — {r.get('score',0)}"
            s = config.font(24).render(txt, True, config.ACCENT)
            self.screen.blit(s, (w//2 - 200, y))
            y += 36

        # back button
        self._btn.center = (w//2, h - 80)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
        b = config.font(20).render("Powrót", True, config.WHITE)
        self.screen.blit(b, b.get_rect(center=self._btn.center))
