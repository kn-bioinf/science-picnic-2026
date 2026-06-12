import pygame
import src.config as config


class MenuScreen:
    """Menu główne: wpisz imię + wybór trybu/ekranu.

    - cała gra (etapy 1->2->3) lub pojedynczy etap,
    - ranking, wiedza na start.
    Enter = zagraj całą grę.
    """

    def __init__(self, screen, state, manager):
        self.screen = screen
        self.state = state
        self.manager = manager
        self.name = "" if state.player_name in ("", "Gracz") else state.player_name
        self._buttons = []     # [(rect, action)] - wypełniane w draw()

    # -------------------------------------------------------------- akcje
    def _commit_name(self):
        self.state.player_name = self.name.strip() or "Gracz"

    def _play_full(self):
        self._commit_name()
        self.manager.play_full()

    def _play_stage(self, n):
        self._commit_name()
        self.manager.play_stage(n)

    # -------------------------------------------------------------- events
    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for rect, action in self._buttons:
                if rect.collidepoint(e.pos):
                    action()
                    return
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                self._play_full()
            elif e.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif e.unicode and e.unicode.isprintable() and len(self.name) < 20:
                self.name += e.unicode

    def update(self, dt):
        pass

    # -------------------------------------------------------------- draw
    def _button(self, cx, cy, w, h, label, action, primary=False, small=False):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (cx, cy)
        col = config.ACCENT if primary else (220, 228, 248)
        pygame.draw.rect(self.screen, col, rect, border_radius=10)
        if not primary:
            pygame.draw.rect(self.screen, config.ACCENT, rect, 2, border_radius=10)
        txt_col = config.WHITE if primary else config.TEXT
        f = config.font(20 if small else 24, bold=primary)
        t = f.render(label, True, txt_col)
        self.screen.blit(t, t.get_rect(center=rect.center))
        self._buttons.append((rect, action))

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)
        self._buttons = []
        cx = w // 2

        title = config.font(48, bold=True).render("Kinezyna na mikrotubuli",
                                                  True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(cx, 70)))
        sub = config.font(20).render("Science Picnic 2026", True, config.MUTED)
        self.screen.blit(sub, sub.get_rect(center=(cx, 110)))

        # pole imienia
        lbl = config.font(18).render("Twoje imię:", True, config.TEXT)
        self.screen.blit(lbl, lbl.get_rect(center=(cx, 158)))
        box = pygame.Rect(0, 0, 360, 52); box.center = (cx, 196)
        pygame.draw.rect(self.screen, (235, 240, 252), box, border_radius=8)
        pygame.draw.rect(self.screen, config.ACCENT, box, 2, border_radius=8)
        shown = self.name if self.name else "Wpisz imię..."
        col = config.TEXT if self.name else config.MUTED
        nm = config.font(26).render(shown, True, col)
        self.screen.blit(nm, nm.get_rect(center=box.center))

        # przyciski
        y = 268
        self._button(cx, y, 360, 56, "Zagraj całą grę", self._play_full,
                     primary=True); y += 70
        self._button(cx, y, 360, 48, "Etap 1: Składanie",
                     lambda: self._play_stage(1), small=True); y += 56
        self._button(cx, y, 360, 48, "Etap 2: Dokowanie",
                     lambda: self._play_stage(2), small=True); y += 56
        self._button(cx, y, 360, 48, "Etap 3: Transport",
                     lambda: self._play_stage(3), small=True); y += 70
        self._button(cx - 95, y, 180, 46, "Ranking",
                     lambda: self.manager.transition_to(self.manager.RANKING),
                     small=True)
        self._button(cx + 95, y, 180, 46, "Wiedza na start",
                     lambda: self.manager.transition_to(self.manager.KNOWLEDGE),
                     small=True)

        hint = config.font(16).render("Enter - zagraj całą grę", True, config.MUTED)
        self.screen.blit(hint, hint.get_rect(center=(cx, y + 50)))
