import pygame
import src.config as config

_STAGE_NAMES = {1: "Etap 1 (składanie)", 2: "Etap 2 (dokowanie)",
                3: "Etap 3 (transport)"}


class EndScreen:
    """Ekran końcowy pełnej gry: wynik łączny + rozbicie na etapy.

    Zapis do rankingu wykonuje GameManager.finish_full — tu tylko wyświetlamy.
    """

    def __init__(self, screen, state, manager):
        self.screen = screen
        self.state = state
        self.manager = manager
        self._btn = pygame.Rect(0, 0, 240, 50)
        self._btn_ranking = pygame.Rect(0, 0, 180, 44)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self._btn.collidepoint(e.pos):
                self.manager.transition_to(self.manager.MENU)
            elif self._btn_ranking.collidepoint(e.pos):
                self.manager.transition_to(self.manager.RANKING)
        elif e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.manager.transition_to(self.manager.MENU)

    def update(self, dt):
        pass

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)
        cx = w // 2

        title = config.font(52, bold=True).render("Koniec gry!", True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(cx, h // 5)))

        score = config.font(34).render(
            f"{self.state.player_name}: {self.state.score} pkt łącznie",
            True, config.ACCENT)
        self.screen.blit(score, score.get_rect(center=(cx, h // 5 + 64)))

        # rozbicie na etapy
        y = h // 5 + 124
        for n in (1, 2, 3):
            sc = self.state.stage_scores.get(n, 0)
            line = config.font(22).render(
                f"{_STAGE_NAMES[n]}: {sc}", True, config.TEXT)
            self.screen.blit(line, line.get_rect(center=(cx, y)))
            y += 32

        # przyciski
        self._btn.center = (cx, h * 3 // 4)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
        b = config.font(22).render("Zagraj ponownie", True, config.WHITE)
        self.screen.blit(b, b.get_rect(center=self._btn.center))

        self._btn_ranking.center = (cx, h * 3 // 4 + 62)
        pygame.draw.rect(self.screen, (220, 228, 248), self._btn_ranking,
                         border_radius=8)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn_ranking, 2,
                         border_radius=8)
        br = config.font(18).render("Ranking", True, config.TEXT)
        self.screen.blit(br, br.get_rect(center=self._btn_ranking.center))

        hint = config.font(15).render("Enter — menu", True, config.MUTED)
        self.screen.blit(hint, hint.get_rect(center=(cx, h - 30)))
