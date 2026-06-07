import pygame
import src.config as config


class EndScreen:
    """Ekran koncowy: wynik gracza + przycisk restart."""

    def __init__(self, screen, state, manager):
        self.screen  = screen
        self.state   = state
        self.manager = manager
        # button position will be computed on draw using current screen size
        self._btn    = pygame.Rect(0, 0, 240, 50)
        self._btn_ranking = pygame.Rect(0, 0, 160, 40)
        self._saved = False

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            if self._btn.collidepoint(e.pos):
                self._restart()
            if self._btn_ranking.collidepoint(e.pos):
                self.manager.transition_to(self.manager.RANKING)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            self._restart()

    def _restart(self):
        self.state.score = 0
        self.manager.transition_to(self.manager.WELCOME)

    def update(self, dt): pass

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)

        title = config.font(52, bold=True).render("Koniec gry!", True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(w // 2, h // 3)))

        score = config.font(32).render(
            f"{self.state.player_name}: {self.state.score} pkt", True, config.ACCENT
        )
        self.screen.blit(score, score.get_rect(center=(w // 2, h // 2)))

        # save ranking once per screen creation
        if not self._saved:
            self.state.save_ranking()
            self._saved = True

        # compute button placement dynamically
        self._btn.center = (w // 2, h * 2 // 3)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
        btn = config.font(22).render("Zagraj ponownie", True, config.WHITE)
        self.screen.blit(btn, btn.get_rect(center=self._btn.center))

        # ranking button
        self._btn_ranking.center = (w // 2, h * 2 // 3 + 70)
        pygame.draw.rect(self.screen, config.MUTED, self._btn_ranking, border_radius=6)
        br = config.font(18).render("Ranking", True, config.WHITE)
        self.screen.blit(br, br.get_rect(center=self._btn_ranking.center))
