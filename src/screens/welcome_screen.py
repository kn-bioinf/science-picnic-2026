import pygame
import src.config as config


class WelcomeScreen:
    """Ekran startowy: wpisz imie, wcisnij Enter aby zaczac."""

    def __init__(self, screen, state, manager):
        self.screen  = screen
        self.state   = state
        self.manager = manager
        self.name    = ""

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN and self.name.strip():
                self.state.player_name = self.name.strip()
                self.state.score = 0
                self.manager.transition_to(self.manager.LEVEL1)
            elif e.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif len(self.name) < 24:
                self.name += e.unicode

    def update(self, dt): pass

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)

        title = config.font(52, bold=True).render("Science Picnic 2026", True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(w // 2, h // 3)))

        box = pygame.Rect(w // 2 - 200, h // 2 - 30, 400, 60)
        pygame.draw.rect(self.screen, (220, 228, 248), box, border_radius=8)
        pygame.draw.rect(self.screen, config.ACCENT, box, 2, border_radius=8)
        label = self.name if self.name else "Wpisz imie..."
        color = config.TEXT if self.name else config.MUTED
        name_surf = config.font(28).render(label, True, color)
        self.screen.blit(name_surf, name_surf.get_rect(center=box.center))

        hint = config.font(20).render("Enter - start", True, config.MUTED)
        self.screen.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 60)))
