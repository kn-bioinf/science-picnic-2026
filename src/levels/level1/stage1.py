# TODO: Zaimplementuj ten etap.
# Gdy etap sie skonczy, wywolaj: self.next(score)

import pygame
import src.config as config


class Stage1:
    """
    Etap 1: skladanie kinezyny (np. wybierz glowy, nogi, ladunek).

    Interfejs:
        __init__(screen, state, next_fn)
        self.next(score: int)  – wywolaj gdy etap skonczony
    """

    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state  = state
        self.next   = next_fn            # wywolaj: self.next(score)
        self._btn   = pygame.Rect(0, 0, 160, 44)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self._btn.collidepoint(e.pos):
            self.next(0)                 # TODO: przekaz prawdziwy wynik

    def update(self, dt):
        pass                             # TODO

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)
        t = config.font(36, bold=True).render("Stage1", True, config.TEXT)
        self.screen.blit(t, t.get_rect(center=(w // 2, h // 2)))
        self._btn.center = (w // 2, h - 90)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
        b = config.font(20).render("Dalej ->", True, config.WHITE)
        self.screen.blit(b, b.get_rect(center=self._btn.center))
