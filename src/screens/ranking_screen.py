import pygame
import src.config as config
from src.game_state import GameState


class RankingScreen:
    """Ranking z 4 zakładkami: Łącznie + Etap 1/2/3."""

    TABS = [("Łącznie", "total"), ("Etap 1", "stage1"),
            ("Etap 2", "stage2"), ("Etap 3", "stage3")]

    def __init__(self, screen, state, manager):
        self.screen = screen
        self.state = state
        self.manager = manager
        self._rankings = GameState.load_rankings()
        self._active = 0
        self._tab_rects = []          # wypełniane w draw()
        self._btn = pygame.Rect(0, 0, 180, 46)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self._btn.collidepoint(e.pos):
                self.manager.transition_to(self.manager.MENU)
                return
            for i, rect in enumerate(self._tab_rects):
                if rect.collidepoint(e.pos):
                    self._active = i
                    return
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.manager.transition_to(self.manager.MENU)
            elif e.key == pygame.K_RIGHT:
                self._active = (self._active + 1) % len(self.TABS)
            elif e.key == pygame.K_LEFT:
                self._active = (self._active - 1) % len(self.TABS)

    def update(self, dt):
        pass

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)
        cx = w // 2

        title = config.font(40, bold=True).render("Ranking", True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(cx, 54)))

        # zakładki
        self._tab_rects = []
        tw, gap = 170, 12
        total_w = len(self.TABS) * tw + (len(self.TABS) - 1) * gap
        x = cx - total_w // 2
        for i, (label, _) in enumerate(self.TABS):
            rect = pygame.Rect(x, 96, tw, 44)
            active = (i == self._active)
            pygame.draw.rect(self.screen, config.ACCENT if active else (220, 228, 248),
                             rect, border_radius=8)
            if not active:
                pygame.draw.rect(self.screen, config.ACCENT, rect, 2, border_radius=8)
            t = config.font(20, bold=active).render(
                label, True, config.WHITE if active else config.TEXT)
            self.screen.blit(t, t.get_rect(center=rect.center))
            self._tab_rects.append(rect)
            x += tw + gap

        # lista wyników
        cat = self.TABS[self._active][1]
        rows = self._rankings.get(cat, [])
        y = 176
        if not rows:
            empty = config.font(22).render("Brak wyników - zagraj!", True, config.MUTED)
            self.screen.blit(empty, empty.get_rect(center=(cx, y + 40)))
        else:
            for i, r in enumerate(rows):
                place = f"{i + 1}."
                name = str(r.get("name", "-"))
                sc = r.get("score", 0)
                col = config.ACCENT if i == 0 else config.TEXT
                f = config.font(24, bold=(i == 0))
                self.screen.blit(f.render(place, True, col), (cx - 220, y))
                self.screen.blit(f.render(name, True, col), (cx - 170, y))
                s_surf = f.render(str(sc), True, col)
                self.screen.blit(s_surf, s_surf.get_rect(topright=(cx + 220, y)))
                y += 34

        # powrót
        self._btn.center = (cx, h - 56)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
        b = config.font(20).render("← Menu", True, config.WHITE)
        self.screen.blit(b, b.get_rect(center=self._btn.center))
        hint = config.font(14).render("← → zmiana zakładki   ·   Enter/Esc - menu",
                                      True, config.MUTED)
        self.screen.blit(hint, hint.get_rect(center=(cx, h - 24)))
