# TODO: Zaimplementuj ten etap.
# Gdy etap sie skonczy, wywolaj: self.next(score)

import pygame
from src.config import W, H, BG, TEXT, ACCENT, WHITE, font


class Stage1:
    """
    Etap 1 poziomu 2 – do zaimplementowania (np. skladanie bialka transbłonowego).

    Interfejs:
        __init__(screen, state, next_fn)
        self.next(score: int)  – wywolaj gdy etap skonczony
    """

    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state  = state
        self.next   = next_fn
        self._btn   = pygame.Rect(W // 2 - 80, H - 90, 160, 44)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self._btn.collidepoint(e.pos):
            self.next(0)

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(BG)
        t = font(36, bold=True).render("Stage1", True, TEXT)
        self.screen.blit(t, t.get_rect(center=(W // 2, H // 2)))
        pygame.draw.rect(self.screen, ACCENT, self._btn, border_radius=8)
        b = font(20).render("Dalej ->", True, WHITE)
        self.screen.blit(b, b.get_rect(center=self._btn.center))
